import 'package:app1/app/app_dependencies_scope.dart';
import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../../chatscreen/controllers/chat_controller.dart';

/// Pill-shaped bottom navigation used on the home screen.
class CustomBottomNav extends StatelessWidget {
  final ValueChanged<int>? onTap;
  final int currentIndex;
  final bool isSimpleView;
  final Key? guideTargetKey;
  final int? historyBadgeCount;

  const CustomBottomNav({
    super.key,
    this.onTap,
    this.currentIndex = 0,
    this.isSimpleView = false,
    this.guideTargetKey,
    this.historyBadgeCount,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final navBackgroundColor = isDarkMode
        ? AppColors.darkElevatedSurface
        : AppColors.lightCard;

    final borderColor = isDarkMode
        ? colorScheme.outlineVariant.withValues(alpha: 0.45)
        : AppColors.careenaInfoBorder;

    final selectedColor = isDarkMode
        ? AppColors.careenaAccentOnDark
        : AppColors.careenaTeal;

    final unselectedColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaSoftAccent;

    final shadowColor = isDarkMode
        ? AppColors.darkBackground.withValues(alpha: 0.18)
        : AppColors.darkBackground.withValues(alpha: 0.05);

    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(15, 0, 15, 12),
      child: Align(
        alignment: Alignment.bottomCenter,
        heightFactor: 1,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Container(
            key: guideTargetKey,
            decoration: BoxDecoration(
              color: navBackgroundColor,
              borderRadius: BorderRadius.circular(40),
              border: Border.all(color: borderColor),
              boxShadow: [
                BoxShadow(
                  color: shadowColor,
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(40),
              child: BottomNavigationBar(
                elevation: 0,
                backgroundColor: AppColors.transparent,
                type: BottomNavigationBarType.fixed,
                selectedItemColor: selectedColor,
                unselectedItemColor: unselectedColor,
                selectedFontSize: isSimpleView ? 16 : 11,
                unselectedFontSize: isSimpleView ? 16 : 11,
                iconSize: isSimpleView ? 32 : 24,
                currentIndex: currentIndex,
                onTap: onTap,
                items: [
                  const BottomNavigationBarItem(
                    icon: Icon(Icons.home_outlined),
                    label: "Startseite",
                  ),
                  const BottomNavigationBarItem(
                    icon: Icon(Icons.calendar_today_outlined),
                    label: "Kalender",
                  ),
                  BottomNavigationBarItem(
                    icon: historyBadgeCount == null
                        ? const _LiveHistoryBadgeIcon()
                        : _HistoryBadgeIcon(count: historyBadgeCount!),
                    label: "Verlauf",
                  ),
                  const BottomNavigationBarItem(
                    icon: Icon(Icons.settings_outlined),
                    label: "Einstellungen",
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _HistoryBadgeIcon extends StatelessWidget {
  final int count;

  const _HistoryBadgeIcon({required this.count});

  @override
  Widget build(BuildContext context) {
    return Badge(
      isLabelVisible: count > 0,
      label: Text(count > 9 ? '9+' : '$count'),
      child: const Icon(Icons.chat_bubble_outline),
    );
  }
}

class _LiveHistoryBadgeIcon extends StatefulWidget {
  const _LiveHistoryBadgeIcon();

  @override
  State<_LiveHistoryBadgeIcon> createState() => _LiveHistoryBadgeIconState();
}

class _LiveHistoryBadgeIconState extends State<_LiveHistoryBadgeIcon> {
  ChatController? _controller;
  int _count = 0;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final nextController = AppDependenciesScope.maybeOf(
      context,
    )?.chatController;
    if (identical(nextController, _controller)) return;

    _controller?.historyRevision.removeListener(_refresh);
    _controller?.authSession.removeListener(_refresh);
    _controller = nextController;
    _controller?.historyRevision.addListener(_refresh);
    _controller?.authSession.addListener(_refresh);
    _refresh();
  }

  Future<void> _refresh() async {
    final controller = _controller;
    final profileId = controller?.authSession.activeProfileId;
    if (controller == null || profileId == null) {
      if (mounted && _count != 0) setState(() => _count = 0);
      return;
    }

    try {
      final entries = await controller.chatHistoryRepository.loadEntries(
        profileId: profileId,
      );
      final count = entries
          .where(
            (entry) =>
                entry.status == 'active' ||
                entry.status == 'waiting_for_assistant',
          )
          .length;
      if (mounted && profileId == controller.authSession.activeProfileId) {
        setState(() => _count = count);
      }
    } catch (_) {}
  }

  @override
  void dispose() {
    _controller?.historyRevision.removeListener(_refresh);
    _controller?.authSession.removeListener(_refresh);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => _HistoryBadgeIcon(count: _count);
}
