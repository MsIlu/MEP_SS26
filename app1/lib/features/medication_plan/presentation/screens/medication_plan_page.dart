import 'package:app1/core/themes/app_colors.dart';
import 'dart:async';

import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../data/medication_api_service.dart';
import '../../data/medication_entry.dart';
import '../../data/medication_repository.dart';
import '../controllers/medication_plan_controller.dart';
import '../widgets/form/medication_form_dialog.dart';
import '../widgets/list/medication_list_dialog.dart';
import '../widgets/layout/medication_plan_content.dart';
import '../../../../core/widgets/careena_page_header.dart';

/// Page for managing personal medications and daily intake reminders.
class MedicationPlanPage extends StatefulWidget {
  final ThemeController themeController;
  final ApiClient? apiClient;
  final AuthSession? authSession;

  const MedicationPlanPage({
    super.key,
    required this.themeController,
    this.apiClient,
    this.authSession,
  });

  @override
  State<MedicationPlanPage> createState() => _MedicationPlanPageState();
}

class _MedicationPlanPageState extends State<MedicationPlanPage> {
  late final MedicationPlanController _controller;

  late final DateTime _today;
  late DateTime _selectedDate;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _today = DateTime(now.year, now.month, now.day);
    _selectedDate = _today;
    _controller = MedicationPlanController(
      repository: MedicationRepository(
        apiService: widget.apiClient == null
            ? null
            : MedicationApiService(widget.apiClient!),
        profileId: widget.authSession?.activeProfileId,
      ),
    );
    _controller.loadEntries();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final horizontalPadding = MediaQuery.sizeOf(context).width < 360
        ? 16.0
        : 20.0;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: CareenaPageHeader(
        title: 'Medikamentenplan',
        trailing: CareenaThemeHeaderAction(
          onPressed: widget.themeController.toggleTheme,
          isDarkMode: widget.themeController.isDarkMode,
        ),
      ),
      body: SafeArea(
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, _) {
            return ResponsivePageBody(
              maxWidth: 720,
              scrollable: false,
              padding: EdgeInsets.fromLTRB(
                horizontalPadding,
                18,
                horizontalPadding,
                14,
              ),
              child: MedicationPlanContent(
                selectedDate: _selectedDate,
                today: _today,
                entries: _controller.entries,
                onDateSelected: (date) {
                  setState(() => _selectedDate = date);
                },
                onOpenMedicationList: _openMedicationList,
                onAddMedication: _openMedicationForm,
                onTakenChanged: _toggleTakenForDate,
              ),
            );
          },
        ),
      ),
    );
  }

  /// Opens a centered form dialog and prepares clean input state first.
  Future<void> _openMedicationForm({MedicationEntry? entry}) async {
    final wasSaved = await showDialog<bool>(
      context: context,
      builder: (context) {
        return MedicationFormDialog(
          initialEntry: entry,
          onSave:
              (
                name,
                dose,
                intakeTime,
                secondIntakeTime,
                frequency,
                remindersEnabled,
                catalogItem,
              ) {
                if (entry != null) {
                  return _controller.updateEntry(
                    entry: entry,
                    name: name,
                    dose: dose,
                    intakeTime: intakeTime,
                    secondIntakeTime: secondIntakeTime,
                    frequency: frequency,
                    remindersEnabled: remindersEnabled,
                    catalogItem: catalogItem,
                  );
                }

                return _controller.addEntry(
                  name: name,
                  dose: dose,
                  intakeTime: intakeTime,
                  secondIntakeTime: secondIntakeTime,
                  frequency: frequency,
                  remindersEnabled: remindersEnabled,
                  catalogItem: catalogItem,
                );
              },
        );
      },
    );

    if (mounted && wasSaved == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            entry == null
                ? 'Medikament gespeichert'
                : 'Medikament aktualisiert',
          ),
        ),
      );
    }
  }

  /// Opens the saved medication list without leaving the current day context.
  Future<void> _openMedicationList() async {
    await showDialog<void>(
      context: context,
      builder: (context) {
        return Dialog(
          insetPadding: const EdgeInsets.all(18),
          backgroundColor: AppColors.transparent,
          child: ResponsiveFrame(
            maxWidth: 720,
            child: Container(
              constraints: const BoxConstraints(maxHeight: 620),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                borderRadius: BorderRadius.circular(20),
              ),
              child: AnimatedBuilder(
                animation: _controller,
                builder: (context, _) {
                  return MedicationListDialog(
                    isLoading: _controller.isLoading,
                    entries: _controller.entries,
                    onAdd: () => _openMedicationFormFromList(context),
                    onClose: () => Navigator.pop(context),
                    onToggleReminder: _toggleReminder,
                    onEdit: (entry) =>
                        _openMedicationEditFormFromList(context, entry),
                    onDelete: _deleteEntry,
                  );
                },
              ),
            ),
          ),
        );
      },
    );
  }

  /// Closes the list dialog before opening the add form to avoid stacked modals.
  Future<void> _openMedicationFormFromList(BuildContext sheetContext) async {
    Navigator.pop(sheetContext);
    await Future<void>.delayed(const Duration(milliseconds: 160));

    if (mounted) {
      await _openMedicationForm();
    }
  }

  /// Closes the list dialog before opening the prefilled edit form.
  Future<void> _openMedicationEditFormFromList(
    BuildContext sheetContext,
    MedicationEntry entry,
  ) async {
    Navigator.pop(sheetContext);
    await Future<void>.delayed(const Duration(milliseconds: 160));

    if (mounted) {
      await _openMedicationForm(entry: entry);
    }
  }

  void _toggleReminder(MedicationEntry entry, bool remindersEnabled) {
    unawaited(
      _runMedicationAction(
        _controller.toggleReminder(entry, remindersEnabled),
        'Erinnerung konnte nicht aktualisiert werden.',
      ),
    );
  }

  void _deleteEntry(MedicationEntry entry) {
    unawaited(
      _runMedicationAction(
        _controller.deleteEntry(entry),
        'Medikament konnte nicht entfernt werden.',
      ),
    );
  }

  void _toggleTakenForDate(
    MedicationEntry entry,
    DateTime date,
    int doseIndex,
    bool isTaken,
  ) {
    unawaited(
      _runMedicationAction(
        _controller.toggleTakenForDate(entry, date, doseIndex, isTaken),
        'Einnahme konnte nicht aktualisiert werden.',
      ),
    );
  }

  Future<void> _runMedicationAction(
    Future<void> action,
    String errorMessage,
  ) async {
    try {
      await action;
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(errorMessage)));
      }
    }
  }
}
