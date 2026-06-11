import 'package:flutter/material.dart';
import '../../../../core/themes/app_colors.dart';
import '../../../../core/themes/theme_controller.dart';
import '../settings_icons.dart';
import 'settings_components.dart';

class DisplaySettingsSection extends StatelessWidget {
  final ThemeController themeController;
  final bool showSimpleView;

  const DisplaySettingsSection({
    super.key,
    required this.themeController,
    this.showSimpleView = true,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (showSimpleView) ...[
          _SimpleViewCard(themeController: themeController),
          const SizedBox(height: 22),
        ],
        const SettingsSectionHeader(
          icon: SettingsIcons.display,
          title: 'Aussehen',
          subtitle: 'Wähle die Einstellung, die du gut erkennen kannst.',
        ),
        const SizedBox(height: 10),
        _ThemeChoice(themeController: themeController),
      ],
    );
  }
}

class _SimpleViewCard extends StatelessWidget {
  final ThemeController themeController;

  const _SimpleViewCard({required this.themeController});

  @override
  Widget build(BuildContext context) {
    final enabled = themeController.isSimpleView;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Semantics(
      button: true,
      toggled: enabled,
      label: 'Einfache Ansicht',
      child: InkWell(
        borderRadius: BorderRadius.circular(28),
        onTap: () => themeController.setSimpleView(!enabled),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: isDark
                ? AppColors.darkElevatedSurface
                : AppColors.careenaBackground,
            borderRadius: BorderRadius.circular(28),
            border: Border.all(
              color: enabled
                  ? AppColors.careenaTeal
                  : AppColors.careenaInfoBorder,
              width: enabled ? 3 : 1.5,
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SettingsIconBadge(
                icon: Icons.accessibility_new,
                isActive: enabled,
                large: true,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            'Einfache Ansicht',
                            style: Theme.of(context).textTheme.titleLarge
                                ?.copyWith(fontWeight: FontWeight.w800),
                          ),
                        ),
                        Switch.adaptive(
                          value: enabled,
                          onChanged: themeController.setSimpleView,
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Größere Schrift, große Schaltflächen und weniger Ablenkung.',
                    ),
                    const SizedBox(height: 12),
                    Text(
                      enabled ? 'Eingeschaltet' : 'Ausgeschaltet',
                      style: TextStyle(
                        color: enabled
                            ? AppColors.careenaTeal
                            : Theme.of(context).colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ThemeChoice extends StatelessWidget {
  final ThemeController themeController;

  const _ThemeChoice({required this.themeController});

  @override
  Widget build(BuildContext context) {
    final choices = ThemeMode.values
        .map(
          (mode) => _ThemeButton(
            mode: mode,
            selected: themeController.themeMode == mode,
            expandedLayout: themeController.isSimpleView,
            onTap: () => themeController.setThemeMode(mode),
          ),
        )
        .toList();

    if (themeController.isSimpleView) {
      return Column(
        children: [
          for (var index = 0; index < choices.length; index++) ...[
            choices[index],
            if (index < choices.length - 1) const SizedBox(height: 10),
          ],
        ],
      );
    }

    return Row(
      children: [
        for (var index = 0; index < choices.length; index++) ...[
          Expanded(child: choices[index]),
          if (index < choices.length - 1) const SizedBox(width: 8),
        ],
      ],
    );
  }
}

class _ThemeButton extends StatelessWidget {
  final ThemeMode mode;
  final bool selected;
  final bool expandedLayout;
  final VoidCallback onTap;

  const _ThemeButton({
    required this.mode,
    required this.selected,
    required this.expandedLayout,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Semantics(
      selected: selected,
      button: true,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: onTap,
        child: Container(
          constraints: BoxConstraints(minHeight: expandedLayout ? 76 : 108),
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 14),
          decoration: BoxDecoration(
            color: selected
                ? (isDark
                      ? AppColors.darkMutedSurface
                      : AppColors.careenaBackground)
                : Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: selected
                  ? AppColors.careenaTeal
                  : AppColors.careenaInfoBorder,
              width: selected ? 3 : 1.5,
            ),
          ),
          child: expandedLayout
              ? _ExpandedThemeChoice(mode: mode, selected: selected)
              : _CompactThemeChoice(mode: mode),
        ),
      ),
    );
  }
}

class _ExpandedThemeChoice extends StatelessWidget {
  final ThemeMode mode;
  final bool selected;

  const _ExpandedThemeChoice({required this.mode, required this.selected});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(_themeIcon(mode), color: AppColors.careenaTeal, size: 34),
        const SizedBox(width: 16),
        Expanded(
          child: Text(
            _themeLabel(mode),
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        Icon(
          selected ? Icons.check_circle : Icons.radio_button_unchecked,
          color: AppColors.careenaTeal,
          size: 30,
        ),
      ],
    );
  }
}

class _CompactThemeChoice extends StatelessWidget {
  final ThemeMode mode;

  const _CompactThemeChoice({required this.mode});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(_themeIcon(mode), color: AppColors.careenaTeal, size: 30),
        const SizedBox(height: 8),
        FittedBox(
          child: Text(
            _themeLabel(mode),
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
      ],
    );
  }
}

IconData _themeIcon(ThemeMode mode) => switch (mode) {
  ThemeMode.system => Icons.brightness_auto,
  ThemeMode.light => Icons.light_mode,
  ThemeMode.dark => Icons.dark_mode,
};

String _themeLabel(ThemeMode mode) => switch (mode) {
  ThemeMode.system => 'Automatisch',
  ThemeMode.light => 'Hell',
  ThemeMode.dark => 'Dunkel',
};
