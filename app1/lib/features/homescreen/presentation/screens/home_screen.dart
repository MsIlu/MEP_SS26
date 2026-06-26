import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/core/widgets/careena_snack_bar.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/features/app_guide/data/app_guide_store.dart';
import 'package:app1/features/app_guide/data/app_guide_steps.dart';
import 'package:app1/features/app_guide/presentation/widgets/app_guide_overlay.dart';
import 'package:app1/features/authscreen/data/auth_api_service.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';

import 'package:app1/features/calendar_overview/presentation/screens/calendar_overview_page.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_screen.dart';
import 'package:app1/features/documents/presentation/screens/documents_screen.dart';
import 'package:app1/features/homescreen/data/home_feature.dart';
import 'package:app1/features/homescreen/presentation/widgets/careena_hero_card.dart';
import 'package:app1/features/homescreen/presentation/widgets/custom_bottom_nav.dart';
import 'package:app1/features/homescreen/presentation/widgets/home_function_list.dart';
import 'package:app1/features/homescreen/presentation/widgets/home_search_bar.dart';
import 'package:app1/features/medication_plan/presentation/screens/medication_plan_page.dart';
import 'package:app1/features/settings/presentation/screens/settings_page.dart';
import '../../../appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:app1/features/symptom_diary/data/symptom_api_service.dart';
import 'package:app1/features/symptom_diary/presentation/screens/symptom_diary_page.dart';
import 'package:flutter/material.dart';
import 'package:app1/features/documents/data/document_repository.dart';

/// Dashboard-style home screen with the Careena entry point and feature list.
class HomeScreen extends StatefulWidget {
  /// Shared chat controller reused when opening the chat from the home screen.
  final ChatController controller;

  /// Shared theme controller used to switch between light and dark mode.
  final ThemeController themeController;
  final ApiClient? apiClient;
  final AuthSession? authSession;
  final AuthApiService? authApiService;
  final bool startGuide;
  final SymptomApiService? symptomApiService;

  const HomeScreen({
    super.key,
    required this.controller,
    required this.themeController,
    this.apiClient,
    this.authSession,
    this.authApiService,
    this.startGuide = false,
    this.symptomApiService,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _careenaKey = GlobalKey();
  final _searchKey = GlobalKey();
  final _featuresKey = GlobalKey();
  final _themeKey = GlobalKey();
  final _navigationKey = GlobalKey();
  int? _guideStep;
  final DocumentRepository _documentRepository = DocumentRepository.instance;

  List<AppGuideStep> get _visibleGuideSteps =>
      widget.themeController.isSimpleView
      ? appGuideSteps
            .where(
              (step) =>
                  step.target != AppGuideTarget.search &&
                  step.target != AppGuideTarget.theme,
            )
            .toList()
      : appGuideSteps;

  @override
  void initState() {
    super.initState();

    _documentRepository.unreadCounts.addListener(_onDocumentBadgeChanged);

    if (widget.startGuide) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _startGuide());
    }
  }

  void _onDocumentBadgeChanged() {
    if (mounted) {
      setState(() {});
    }
  }

  @override
  void dispose() {
    _documentRepository.unreadCounts.removeListener(_onDocumentBadgeChanged);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([
        widget.themeController,
        if (widget.authSession != null) widget.authSession!,
      ]),
      builder: (context, _) {
        final features = _buildFeatures(context);
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;
        final isCompact = MediaQuery.sizeOf(context).width < 360;

        return Stack(
          children: [
            Scaffold(
              backgroundColor: isDarkMode
                  ? Theme.of(context).scaffoldBackgroundColor
                  : AppColors.headerBackgroundLight,
              appBar: CareenaPageHeader(
                title: _welcomeTitle,
                showBack: false,
                leading: CareenaHeaderAction(
                  tooltip: 'App-Guide testen',
                  icon: Icons.help_outline,
                  onPressed: _startGuide,
                ),
                trailing: widget.themeController.isSimpleView
                    ? null
                    : CareenaThemeHeaderAction(
                        key: _themeKey,
                        onPressed: widget.themeController.toggleTheme,
                        isDarkMode: widget.themeController.isDarkMode,
                      ),
              ),
              body: SafeArea(
                child: ResponsivePageBody(
                  maxWidth: 720,
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        CareenaHeroCard(
                          guideTargetKey: _careenaKey,
                          onTap: () => _navigateToChat(context),
                          isSimpleView: widget.themeController.isSimpleView,
                        ),
                        if (!widget.themeController.isSimpleView)
                          HomeSearchBar(
                            guideTargetKey: _searchKey,
                            isCompact: isCompact,
                          ),
                        HomeFunctionList(
                          guideTargetKey: _featuresKey,
                          features: features,
                          isSimpleView: widget.themeController.isSimpleView,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              bottomNavigationBar: CustomBottomNav(
                guideTargetKey: _navigationKey,
                currentIndex: 0,
                isSimpleView: widget.themeController.isSimpleView,
                onTap: (index) => _onBottomNavigationTap(context, index),
              ),
            ),
            if (_guideStep != null)
              AppGuideOverlay(
                targetKey: _targetKey(_visibleGuideSteps[_guideStep!].target),
                step: _visibleGuideSteps[_guideStep!],
                currentStep: _guideStep!,
                stepCount: _visibleGuideSteps.length,
                onPrevious: _guideStep == 0 ? null : _previousGuideStep,
                onNext: _nextGuideStep,
                onSkip: _finishGuide,
              ),
          ],
        );
      },
    );
  }

  String get _welcomeTitle {
    final name = widget.authSession?.activeProfile?.displayName.trim();
    if (name == null || name.isEmpty) {
      return 'Willkommen!';
    }
    final firstName = name.split(RegExp(r'\s+')).first;
    return 'Willkommen $firstName!';
  }

  void _onBottomNavigationTap(BuildContext context, int index) {
    if (index == 0) {
      return;
    }

    if (index == 1) {
      _navigateToCalendar(context);
    } else if (index == 2) {
      _navigateToChatHistory(context);
    } else if (index == 3) {
      _openSettings(context);
    }
  }

  void _navigateToChatHistory(BuildContext context) {
    final activeProfileId = widget.controller.authSession.activeProfileId;

    if (activeProfileId == null) {
      showCareenaSnackBar(
        context,
        'Melde dich an, um gespeicherte Verläufe zu sehen.',
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatHistoryScreen(
          themeController: widget.themeController,
          profileId: activeProfileId,
          repository: widget.controller.chatHistoryRepository,
        ),
      ),
    );
  }

  void _openSettings(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SettingsPage(
          themeController: widget.themeController,
          authSession: widget.authSession,
          authApiService: widget.authApiService,
          profileApiService: _dependenciesFromContext(
            context,
          )?.dependencies.profileApiService,
        ),
      ),
    );
  }

  void _startGuide() {
    if (!mounted) return;
    setState(() => _guideStep = 0);
  }

  void _nextGuideStep() {
    final nextStep = (_guideStep ?? 0) + 1;
    if (nextStep >= _visibleGuideSteps.length) {
      _finishGuide();
      return;
    }
    setState(() => _guideStep = nextStep);
  }

  void _previousGuideStep() {
    if ((_guideStep ?? 0) == 0) return;
    setState(() => _guideStep = _guideStep! - 1);
  }

  Future<void> _finishGuide() async {
    setState(() => _guideStep = null);
    final accountId = widget.authSession?.account?.id;
    final userKey = accountId == null
        ? AppGuideStore.guestKey
        : AppGuideStore.accountKey(accountId);
    await AppGuideStore().markCompleted(userKey);
  }

  GlobalKey _targetKey(AppGuideTarget target) => switch (target) {
    AppGuideTarget.careena => _careenaKey,
    AppGuideTarget.search => _searchKey,
    AppGuideTarget.features => _featuresKey,
    AppGuideTarget.theme => _themeKey,
    AppGuideTarget.navigation => _navigationKey,
  };

  void _navigateToChat(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatScreen(
          controller: widget.controller,
          themeController: widget.themeController,
        ),
      ),
    );
  }

  List<HomeFeature> _buildFeatures(BuildContext context) {
    const featureColor = AppColors.careenaInfoBorder;
    final activeProfileId =
        widget.authSession?.activeProfileId ??
        _dependenciesFromContext(
          context,
        )?.dependencies.authSession.activeProfileId;

    return [
      HomeFeature(
        icon: Icons.menu_book_outlined,
        title: 'Symptomtagebuch',
        backgroundColor: featureColor,
        onTap: () => _navigateToSymptomDiary(context),
      ),
      HomeFeature(
        icon: Icons.medication,
        title: 'Medikamententagebuch',
        backgroundColor: featureColor,
        onTap: () => _navigateToMedicationPlan(context),
      ),
      HomeFeature(
        icon: Icons.access_time,
        title: 'Terminplanung',
        backgroundColor: featureColor,
        onTap: () => _navigateToAppointments(context),
      ),
      HomeFeature(
        icon: Icons.description_outlined,
        title: 'Dokumente',
        backgroundColor: featureColor,
        badgeCount: _documentRepository.unreadCountForProfile(activeProfileId),
        onTap: () => _navigateToDocuments(context),
      ),
      HomeFeature(
        icon: Icons.health_and_safety_outlined,
        title: 'Präventive Angebote',
        backgroundColor: featureColor,
        onTap: () {},
      ),
    ];
  }

  void _navigateToMedicationPlan(BuildContext context) {
    final dependencies = _dependenciesFromContext(context);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => MedicationPlanPage(
          themeController: widget.themeController,
          apiClient: widget.apiClient ?? dependencies?.dependencies.apiClient,
          authSession:
              widget.authSession ?? dependencies?.dependencies.authSession,
        ),
      ),
    );
  }

  void _navigateToSymptomDiary(BuildContext context) {
    final dependencies = _dependenciesFromContext(context);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SymptomDiaryPage(
          themeController: widget.themeController,
          authSession:
              widget.authSession ?? dependencies?.dependencies.authSession,
          symptomApiService:
              widget.symptomApiService ??
              dependencies?.dependencies.symptomApiService,
        ),
      ),
    );
  }

  void _navigateToAppointments(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AppointmentScreen(
          themeController: widget.themeController,
          authSession:
          widget.authSession ?? dependencies?.dependencies.authSession,

        ),
      ),
    );
  }

  void _navigateToCalendar(BuildContext context) {
    final dependencies = _dependenciesFromContext(context);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CalendarOverviewPage(
          themeController: widget.themeController,
          apiClient: widget.apiClient ?? dependencies?.dependencies.apiClient,
          authSession:
              widget.authSession ?? dependencies?.dependencies.authSession,
        ),
      ),
    );
  }

  void _navigateToDocuments(BuildContext context) {
    final dependencies = _dependenciesFromContext(context);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DocumentsScreen(
          authSession:
          widget.authSession ?? dependencies?.dependencies.authSession,
        ),
      ),
    );
  }

  AppDependenciesScope? _dependenciesFromContext(BuildContext context) {
    return context
            .getElementForInheritedWidgetOfExactType<AppDependenciesScope>()
            ?.widget
        as AppDependenciesScope?;
  }
}
