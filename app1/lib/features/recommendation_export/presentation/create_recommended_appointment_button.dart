import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/network/api_exception.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/features/appointmentscreen/controllers/appointment_controller.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:app1/features/appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/recommendation_export/data/appointment_search_api_service.dart';
import 'package:flutter/material.dart';

class CreateRecommendedAppointmentButton extends StatelessWidget {
  final AuthSession? authSession;
  final String title;
  final String? sessionId;
  final bool alreadySearched;
  final Future<void> Function()? onSearched;

  /// Profile resolved by the backend session. Null means the session was not
  /// profile-bound — the button will block with an info dialog instead of
  /// silently associating the appointment with the app's active profile.
  final int? profileId;

  const CreateRecommendedAppointmentButton({
    super.key,
    required this.title,
    this.authSession,
    this.sessionId,
    this.alreadySearched = false,
    this.onSearched,
    this.profileId,
  });

  @override
  Widget build(BuildContext context) {
    final profileId =
        this.profileId ??
        (authSession?.isAuthenticated == true
            ? authSession?.activeProfileId
            : null);
    return ValueListenableBuilder<List<Appointment>>(
      valueListenable: AppointmentController().appointments,
      builder: (context, appointments, _) {
        final hasActiveBooking = appointments.any(
          (appointment) =>
              appointment.isRecommendation &&
              appointment.profileId == profileId &&
              (sessionId == null || appointment.sessionId == sessionId),
        );
        return _AsyncAppointmentButton(
          isCompleted: hasActiveBooking,
          onPressed: () => _handlePressed(context),
          builder: _buildButton,
        );
      },
    );
  }

  Widget _buildButton(
    bool isLoading,
    bool isCompleted,
    VoidCallback? onPressed,
  ) {
    return Tooltip(
      message: isCompleted
          ? 'Termin bereits gebucht – siehe Terminplanung'
          : 'Termin suchen und buchen',
      child: OutlinedButton.icon(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.careenaTeal,
          side: const BorderSide(color: AppColors.careenaTeal),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
        ),
        icon: isLoading
            ? const SizedBox.square(
                dimension: 18,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Icon(
                isCompleted
                    ? Icons.check_circle_outline
                    : Icons.event_available_outlined,
              ),
        label: Text(
          isCompleted
              ? 'Bereits gebucht'
              : sessionId == null
              ? 'Termin erstellen'
              : 'Termin finden',
        ),
        onPressed: onPressed,
      ),
    );
  }

  Future<bool> _handlePressed(BuildContext context) async {
    final profileId =
        this.profileId ??
        (authSession?.isAuthenticated == true
            ? authSession?.activeProfileId
            : null);

    if (sessionId == null && profileId == null) {
      await _showInfoDialog(
        context,
        title: 'Kein Profil ausgewählt',
        message:
            'Bitte wähle zuerst ein Profil aus, damit der Termin korrekt zugeordnet werden kann.',
      );
      return false;
    }

    if (sessionId == null) {
      return _createFallbackAppointment(context, profileId!);
    }

    final postalCode = await _askForPostalCode(context);

    if (postalCode == null) {
      return false;
    }

    if (!context.mounted) return false;

    return _searchAndSelectAppointment(
      context: context,
      profileId: profileId,
      postalCode: postalCode,
    );
  }

  Future<bool> _searchAndSelectAppointment({
    required BuildContext context,
    required int? profileId,
    required String postalCode,
  }) async {
    final apiClient = AppDependenciesScope.of(context).apiClient;
    final appointmentSearchApi = AppointmentSearchApiService(apiClient);

    _showLoadingDialog(context);

    AppointmentSearchResponse response;

    try {
      response = await appointmentSearchApi.search(
        sessionId: sessionId!,
        profileId: profileId,
        postalCode: postalCode,
      );
    } catch (e) {
      if (context.mounted) {
        Navigator.pop(context);
        final error = _appointmentError(e, operation: 'search');
        await _showInfoDialog(
          context,
          title: error.title,
          message: error.message,
        );
      }
      return false;
    }

    if (!context.mounted) return false;
    Navigator.pop(context);

    if (response.appointments.isEmpty) {
      await _showInfoDialog(
        context,
        title: 'Keine regulären Termine',
        message: response.message,
      );
      return false;
    }

    if (!context.mounted) return false;

    final selectedAppointment = await _showAppointmentSelectionDialog(
      context,
      response,
    );

    if (selectedAppointment == null) {
      return false;
    }
    if (!context.mounted) return false;

    if (authSession?.isAuthenticated != true || profileId == null) {
      await _showInfoDialog(
        context,
        title: 'Anmeldung erforderlich',
        message:
            'Die Terminsuche ist ohne Anmeldung möglich. Um den ausgewählten Termin verbindlich zu buchen und in deiner Terminplanung zu speichern, melde dich bitte an.',
      );
      return false;
    }

    final note = _buildAppointmentNote(selectedAppointment);

    Appointment appointment;

    try {
      appointment = await appointmentSearchApi.saveRecommendedAppointment(
        profileId: profileId,
        sessionId: sessionId!,
        appointment: selectedAppointment,
        note: note,
      );
    } catch (e) {
      if (context.mounted) {
        final error = _appointmentError(e, operation: 'booking');
        await _showInfoDialog(
          context,
          title: error.title,
          message: error.message,
        );
      }
      return false;
    }

    // Persist the completed action only after HAPI booking and backend save.
    await onSearched?.call();

    final controller = AppointmentController();
    final wasCreated = controller.addRecommendedAppointmentIfMissing(
      appointment,
    );

    if (!wasCreated) {
      controller.upsertRecommendedAppointments([appointment]);
    }

    if (!context.mounted) return false;

    await _showAppointmentSavedDialog(
      context: context,
      appointment: appointment,
      wasCreated: wasCreated,
    );
    return true;
  }

  Future<bool> _createFallbackAppointment(
    BuildContext context,
    int profileId,
  ) async {
    final appointment = Appointment(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      profileId: profileId,
      doctorName: title,
      note: 'Von Careena empfohlen',
      isRecommendation: true,
    );

    final wasCreated = AppointmentController()
        .addRecommendedAppointmentIfMissing(appointment);

    await onSearched?.call();

    if (!context.mounted) return false;

    await _showAppointmentSavedDialog(
      context: context,
      appointment: appointment,
      wasCreated: wasCreated,
    );
    return true;
  }

  Future<String?> _askForPostalCode(BuildContext context) async {
    final postalCodeController = TextEditingController();
    String? errorText;

    final result = await showDialog<String>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            final isDarkMode = Theme.of(context).brightness == Brightness.dark;
            final colorScheme = Theme.of(context).colorScheme;

            return AlertDialog(
              backgroundColor: colorScheme.surface,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(24),
              ),
              titlePadding: const EdgeInsets.fromLTRB(24, 24, 24, 8),
              contentPadding: const EdgeInsets.fromLTRB(24, 8, 24, 8),
              actionsPadding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
              title: Row(
                children: [
                  Container(
                    width: 42,
                    height: 42,
                    decoration: BoxDecoration(
                      color: isDarkMode
                          ? AppColors.careenaDark
                          : AppColors.careenaBubbleBackground,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Icon(
                      Icons.event_available_outlined,
                      color: AppColors.careenaTeal,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Termin finden',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w800,
                        color: isDarkMode
                            ? AppColors.darkTextPrimary
                            : AppColors.careenaTitle,
                      ),
                    ),
                  ),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Gib deine Postleitzahl ein. Careena fragt dann passende '
                    'Termine beim simulierten 116117-Terminservice ab.',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      height: 1.35,
                      color: isDarkMode
                          ? AppColors.darkTextSecondary
                          : AppColors.careenaBody,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.info_outline,
                        size: 15,
                        color: AppColors.careenaTeal,
                      ),
                      SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          'Demo: Simulierter 116117-Terminservice – keine echten Arzttermine.',
                          style: TextStyle(
                            fontSize: 11,
                            color: AppColors.careenaTeal,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: postalCodeController,
                    keyboardType: TextInputType.number,
                    maxLength: 5,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                    decoration: InputDecoration(
                      labelText: 'PLZ',
                      hintText: 'z. B. 68159',
                      errorText: errorText,
                      counterText: '',
                      filled: true,
                      fillColor: isDarkMode
                          ? AppColors.darkMutedSurface
                          : AppColors.symptomListSurfaceLight,
                      prefixIcon: const Icon(
                        Icons.location_on_outlined,
                        color: AppColors.careenaTeal,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide(
                          color: isDarkMode
                              ? AppColors.careenaAccentOnDark.withValues(
                                  alpha: 0.35,
                                )
                              : AppColors.careenaBorder,
                        ),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: const BorderSide(
                          color: AppColors.careenaTeal,
                          width: 1.6,
                        ),
                      ),
                    ),
                    onChanged: (_) {
                      if (errorText == null) return;
                      setDialogState(() {
                        errorText = null;
                      });
                    },
                  ),
                ],
              ),
              actions: [
                TextButton(
                  style: TextButton.styleFrom(
                    foregroundColor: AppColors.careenaTeal,
                    textStyle: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  onPressed: () => Navigator.pop(dialogContext),
                  child: const Text('Abbrechen'),
                ),
                FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: AppColors.careenaTeal,
                    foregroundColor: AppColors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 18,
                      vertical: 12,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  onPressed: () {
                    final postalCode = postalCodeController.text.trim();

                    if (!RegExp(r'^\d{5}$').hasMatch(postalCode)) {
                      setDialogState(() {
                        errorText =
                            'Bitte gib eine gültige 5-stellige PLZ ein.';
                      });
                      return;
                    }

                    Navigator.pop(dialogContext, postalCode);
                  },
                  child: const Text('Suchen'),
                ),
              ],
            );
          },
        );
      },
    );

    postalCodeController.dispose();
    return result;
  }

  Future<FhirAppointmentResult?> _showAppointmentSelectionDialog(
    BuildContext context,
    AppointmentSearchResponse response,
  ) async {
    return showDialog<FhirAppointmentResult>(
      context: context,
      builder: (dialogContext) {
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;
        final colorScheme = Theme.of(context).colorScheme;

        return AlertDialog(
          backgroundColor: colorScheme.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          titlePadding: const EdgeInsets.fromLTRB(24, 24, 24, 8),
          contentPadding: const EdgeInsets.fromLTRB(20, 8, 20, 8),
          actionsPadding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
          title: Text(
            'Passende Termine',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w900,
              color: isDarkMode
                  ? AppColors.darkTextPrimary
                  : AppColors.careenaTitle,
            ),
          ),
          content: SizedBox(
            width: 460,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Padding(
                      padding: EdgeInsets.only(bottom: 12),
                      child: Text(
                        'ⓘ Simulierter 116117-Terminservice – keine echten Arzttermine',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppColors.careenaTeal,
                        ),
                      ),
                    ),
                  ),
                  ...response.appointments.map((appointment) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: InkWell(
                        borderRadius: BorderRadius.circular(20),
                        onTap: () {
                          Navigator.pop(dialogContext, appointment);
                        },
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: isDarkMode
                                ? AppColors.appointmentServiceCardDark
                                : AppColors.appointmentServiceCardLight,
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: isDarkMode
                                  ? AppColors.careenaAccentOnDark.withValues(
                                      alpha: 0.35,
                                    )
                                  : AppColors.careenaBorder,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: AppColors.black.withValues(
                                  alpha: isDarkMode ? 0.16 : 0.05,
                                ),
                                blurRadius: 10,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                width: 44,
                                height: 44,
                                decoration: BoxDecoration(
                                  color: isDarkMode
                                      ? AppColors.darkMutedSurface
                                      : AppColors.appointmentInfoBackground,
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                child: const Icon(
                                  Icons.local_hospital_outlined,
                                  color: AppColors.careenaTeal,
                                ),
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      appointment.providerName,
                                      style: Theme.of(context)
                                          .textTheme
                                          .titleMedium
                                          ?.copyWith(
                                            fontWeight: FontWeight.w900,
                                            color: isDarkMode
                                                ? AppColors.darkTextPrimary
                                                : AppColors.careenaTitle,
                                          ),
                                    ),
                                    const SizedBox(height: 6),
                                    Text(
                                      appointment.specialty,
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyMedium
                                          ?.copyWith(
                                            fontWeight: FontWeight.w700,
                                            color: AppColors.careenaTeal,
                                          ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      '${appointment.date} um ${appointment.time} Uhr',
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyMedium
                                          ?.copyWith(
                                            color: isDarkMode
                                                ? AppColors.darkTextSecondary
                                                : AppColors.careenaBody,
                                          ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      appointment.address,
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyMedium
                                          ?.copyWith(
                                            color: isDarkMode
                                                ? AppColors.darkTextSecondary
                                                : AppColors.careenaBody,
                                          ),
                                    ),
                                    const SizedBox(height: 10),
                                    Wrap(
                                      spacing: 8,
                                      runSpacing: 8,
                                      children: [
                                        _CareenaAppointmentChip(
                                          icon: Icons.directions_walk_outlined,
                                          text:
                                              '${appointment.distanceKm.toStringAsFixed(1)} km',
                                        ),
                                        _CareenaAppointmentChip(
                                          icon: Icons.medical_services_outlined,
                                          text: appointment.careType,
                                        ),
                                        if (appointment.urgencyMatch)
                                          const _CareenaAppointmentChip(
                                            icon: Icons.check_circle_outline,
                                            text: 'passt zur Dringlichkeit',
                                          ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(width: 8),
                              const Icon(
                                Icons.chevron_right_rounded,
                                color: AppColors.careenaTeal,
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              style: TextButton.styleFrom(
                foregroundColor: AppColors.careenaTeal,
                textStyle: const TextStyle(fontWeight: FontWeight.w700),
              ),
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Abbrechen'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _showAppointmentSavedDialog({
    required BuildContext context,
    required Appointment appointment,
    required bool wasCreated,
  }) async {
    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;
        final colorScheme = Theme.of(context).colorScheme;

        return AlertDialog(
          backgroundColor: colorScheme.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          title: Text(
            wasCreated
                ? 'Termin hinzugefügt'
                : 'Terminempfehlung bereits vorhanden',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w900,
              color: isDarkMode
                  ? AppColors.darkTextPrimary
                  : AppColors.careenaTitle,
            ),
          ),
          content: Text(
            wasCreated
                ? 'Der Termin wurde deiner Terminplanung hinzugefügt.'
                : 'Diese Empfehlung ist bereits in deiner Terminplanung vorhanden.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              height: 1.35,
              color: isDarkMode
                  ? AppColors.darkTextSecondary
                  : AppColors.careenaBody,
            ),
          ),
          actions: [
            TextButton(
              style: TextButton.styleFrom(
                foregroundColor: AppColors.careenaTeal,
                textStyle: const TextStyle(fontWeight: FontWeight.w700),
              ),
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Hier bleiben'),
            ),
            FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.careenaTeal,
                foregroundColor: AppColors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              onPressed: () {
                Navigator.pop(dialogContext);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => AppointmentScreen(
                      authSession: authSession,
                      initialAppointmentId: appointment.id,
                    ),
                  ),
                );
              },
              child: const Text('Zur Terminplanung'),
            ),
          ],
        );
      },
    );
  }

  void _showLoadingDialog(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final colorScheme = Theme.of(context).colorScheme;

    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (_) {
        return AlertDialog(
          backgroundColor: colorScheme.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          content: Row(
            children: [
              const CircularProgressIndicator(color: AppColors.careenaTeal),
              const SizedBox(width: 18),
              Expanded(
                child: Text(
                  'Careena fragt den 116117-Terminservice nach passenden Terminen...',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: isDarkMode
                        ? AppColors.darkTextPrimary
                        : AppColors.careenaBody,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _showInfoDialog(
    BuildContext context, {
    required String title,
    required String message,
  }) async {
    if (!context.mounted) return;

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;
        final colorScheme = Theme.of(context).colorScheme;

        return AlertDialog(
          backgroundColor: colorScheme.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          title: Text(
            title,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w900,
              color: isDarkMode
                  ? AppColors.darkTextPrimary
                  : AppColors.careenaTitle,
            ),
          ),
          content: Text(
            message,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              height: 1.35,
              color: isDarkMode
                  ? AppColors.darkTextSecondary
                  : AppColors.careenaBody,
            ),
          ),
          actions: [
            FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.careenaTeal,
                foregroundColor: AppColors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  String _buildAppointmentNote(FhirAppointmentResult appointment) {
    return 'Von Careena empfohlen\n'
        'Fachrichtung: ${appointment.specialty}\n'
        'Versorgungsart: ${appointment.careType}\n'
        'Adresse: ${appointment.address}\n'
        'Entfernung: ${appointment.distanceKm.toStringAsFixed(1)} km\n'
        'Quelle: Simulierter 116117-Terminservice';
  }
}

class _AsyncAppointmentButton extends StatefulWidget {
  final bool isCompleted;
  final Future<bool> Function() onPressed;
  final Widget Function(
    bool isLoading,
    bool isCompleted,
    VoidCallback? onPressed,
  )
  builder;

  const _AsyncAppointmentButton({
    required this.isCompleted,
    required this.onPressed,
    required this.builder,
  });

  @override
  State<_AsyncAppointmentButton> createState() =>
      _AsyncAppointmentButtonState();
}

class _AsyncAppointmentButtonState extends State<_AsyncAppointmentButton> {
  bool _isLoading = false;
  late bool _isCompleted;

  @override
  void initState() {
    super.initState();
    _isCompleted = widget.isCompleted;
  }

  @override
  void didUpdateWidget(covariant _AsyncAppointmentButton oldWidget) {
    super.didUpdateWidget(oldWidget);
    _isCompleted = widget.isCompleted;
  }

  @override
  Widget build(BuildContext context) {
    return widget.builder(
      _isLoading,
      _isCompleted,
      _isCompleted || _isLoading ? null : _run,
    );
  }

  Future<void> _run() async {
    setState(() => _isLoading = true);
    try {
      final completed = await widget.onPressed();
      if (mounted && completed) setState(() => _isCompleted = true);
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Der Aktionsstatus konnte nicht gespeichert werden'),
        ),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
}

class _CareenaAppointmentChip extends StatelessWidget {
  final IconData icon;
  final String text;

  const _CareenaAppointmentChip({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: isDarkMode
            ? AppColors.darkMutedSurface
            : AppColors.careenaBubbleBackground,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: isDarkMode
              ? AppColors.careenaAccentOnDark.withValues(alpha: 0.28)
              : AppColors.careenaInfoBorder,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 15, color: AppColors.careenaTeal),
          const SizedBox(width: 6),
          Text(
            text,
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
              color: isDarkMode
                  ? AppColors.darkTextPrimary
                  : AppColors.careenaTitle,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}

class _AppointmentErrorPresentation {
  final String title;
  final String message;

  const _AppointmentErrorPresentation(this.title, this.message);
}

_AppointmentErrorPresentation _appointmentError(
  Object error, {
  required String operation,
}) {
  final fallbackTitle = operation == 'booking'
      ? 'Terminbuchung fehlgeschlagen'
      : 'Terminsuche fehlgeschlagen';

  if (error is! ApiException) {
    return _AppointmentErrorPresentation(
      fallbackTitle,
      'Es ist ein unerwarteter Fehler aufgetreten. Bitte versuche es erneut.',
    );
  }

  if (error.type == ApiErrorType.network) {
    return const _AppointmentErrorPresentation(
      'Careena-Server nicht erreichbar',
      'Es konnte keine Verbindung zum Careena-Server hergestellt werden. Bitte prüfe, ob das Backend läuft.',
    );
  }
  if (error.type == ApiErrorType.timeout) {
    return const _AppointmentErrorPresentation(
      'Zeitüberschreitung bei der Terminsuche',
      'Die Terminsuche hat zu lange gedauert. Bitte warte kurz und versuche es erneut.',
    );
  }
  if (error.type == ApiErrorType.invalidResponse) {
    return const _AppointmentErrorPresentation(
      'Ungültige Serverantwort',
      'Der Careena-Server hat eine unvollständige Antwort geliefert. Bitte starte die Suche erneut.',
    );
  }

  final detail = _userFriendlyAppointmentDetail(error.message);
  final normalized = detail.toLowerCase();
  switch (error.statusCode) {
    case 401:
      return const _AppointmentErrorPresentation(
        'Anmeldung erforderlich',
        'Deine Sitzung ist abgelaufen. Bitte melde dich erneut an.',
      );
    case 403:
      return const _AppointmentErrorPresentation(
        'Keine Berechtigung für dieses Profil',
        'Du darfst für das ausgewählte Profil keine Termine suchen oder buchen.',
      );
    case 409:
      if (normalized.contains('not linked to a profile')) {
        return const _AppointmentErrorPresentation(
          'Chat ist keinem Profil zugeordnet',
          'Öffne einen Chat für das gewünschte Profil und fordere dort erneut eine Handlungsempfehlung an.',
        );
      }
      if (normalized.contains('different profile') ||
          normalized.contains('does not match')) {
        return const _AppointmentErrorPresentation(
          'Falsches Profil ausgewählt',
          'Die Handlungsempfehlung gehört zu einem anderen Profil. Wechsle zurück zum ursprünglichen Profil.',
        );
      }
      if (normalized.contains('no careena recommendation')) {
        return const _AppointmentErrorPresentation(
          'Keine Handlungsempfehlung vorhanden',
          'Für diesen Chat wurde noch keine Handlungsempfehlung erstellt. Fordere sie zuerst im Chat an.',
        );
      }
      if (normalized.contains('bereits gebucht')) {
        return const _AppointmentErrorPresentation(
          'Termin nicht mehr verfügbar',
          'Der ausgewählte Termin wurde inzwischen gebucht. Bitte wähle einen anderen Termin.',
        );
      }
      return _AppointmentErrorPresentation(fallbackTitle, detail);
    case 422:
      return const _AppointmentErrorPresentation(
        'Ungültige Suchangaben',
        'Bitte gib eine gültige fünfstellige Postleitzahl ein.',
      );
    case 502:
    case 503:
    case 504:
      return _AppointmentErrorPresentation(
        'Terminservice nicht erreichbar',
        'Der simulierte 116117-Terminservice ist momentan nicht erreichbar. Bitte versuche es später erneut.',
      );
    default:
      return _AppointmentErrorPresentation(fallbackTitle, detail);
  }
}

String _userFriendlyAppointmentDetail(String detail) {
  return detail
      .replaceAll(RegExp('HAPI-FHIR', caseSensitive: false), 'Terminservice')
      .replaceAll(RegExp('HAPI', caseSensitive: false), 'Terminservice')
      .replaceAll(RegExp('FHIR-Resource', caseSensitive: false), 'Termindaten')
      .replaceAll(RegExp('FHIR-Termin', caseSensitive: false), 'Termin');
}
