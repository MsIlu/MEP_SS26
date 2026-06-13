import 'package:flutter/material.dart';

import '../../../../core/themes/app_colors.dart';

class SettingsSectionHeader extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const SettingsSectionHeader({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SettingsIconBadge(icon: icon),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
              ),
              Text(
                subtitle,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class SettingsPanel extends StatelessWidget {
  final List<Widget> children;

  const SettingsPanel({super.key, required this.children});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Material(
      clipBehavior: Clip.antiAlias,
      color: isDark
          ? AppColors.darkElevatedSurface
          : AppColors.careenaNoteBackground,
      borderRadius: BorderRadius.circular(18),
      child: Column(
        children: [
          for (var index = 0; index < children.length; index++) ...[
            children[index],
            if (index < children.length - 1)
              Divider(
                height: 1,
                indent: 58,
                color: isDark
                    ? Theme.of(context).colorScheme.outlineVariant
                    : AppColors.careenaBorder,
              ),
          ],
        ],
      ),
    );
  }
}

class SettingsLinkTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final Widget page;

  const SettingsLinkTile({
    super.key,
    required this.icon,
    required this.title,
    required this.description,
    required this.page,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: SettingsIconBadge(icon: icon),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
      subtitle: Text(description),
      trailing: const Icon(Icons.chevron_right, color: AppColors.careenaTeal),
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => page),
      ),
    );
  }
}

class SettingsIconBadge extends StatelessWidget {
  final IconData icon;
  final bool isActive;
  final bool large;

  const SettingsIconBadge({
    super.key,
    required this.icon,
    this.isActive = false,
    this.large = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(large ? 14 : 10),
      decoration: BoxDecoration(
        color: isActive ? AppColors.careenaTeal : AppColors.careenaInfoBorder,
        borderRadius: BorderRadius.circular(large ? 18 : 14),
      ),
      child: Icon(
        icon,
        size: large ? 32 : 24,
        color: isActive
            ? AppColors.toolbarButtonForeground
            : AppColors.careenaDark,
      ),
    );
  }
}

class SettingsMenuTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? description;
  final Widget? trailing;
  final VoidCallback? onTap;
  final bool isSimpleView;

  const SettingsMenuTile({
    super.key,
    required this.icon,
    required this.title,
    this.description,
    this.trailing,
    this.onTap,
    this.isSimpleView = false,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      minTileHeight: isSimpleView ? 76 : 62,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
      leading: Icon(
        icon,
        color: AppColors.careenaTeal,
        size: isSimpleView ? 30 : 25,
      ),
      title: Text(
        title,
        style: TextStyle(
          fontSize: isSimpleView ? 19 : 16,
          fontWeight: FontWeight.w700,
        ),
      ),
      subtitle: description == null
          ? null
          : Text(
              description!,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
      trailing:
          trailing ??
          const Icon(Icons.chevron_right, color: AppColors.careenaMuted),
      onTap: onTap,
    );
  }
}

class SettingsSearchField extends StatelessWidget {
  final TextEditingController controller;
  final ValueChanged<String> onChanged;
  final bool simpleView;

  const SettingsSearchField({
    super.key,
    required this.controller,
    required this.onChanged,
    required this.simpleView,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return TextField(
      controller: controller,
      onChanged: onChanged,
      style: TextStyle(fontSize: simpleView ? 18 : 16),
      decoration: InputDecoration(
        hintText: 'Einstellung suchen...',
        prefixIcon: const Icon(Icons.search, color: AppColors.careenaTeal),
        suffixIcon: controller.text.isEmpty
            ? null
            : IconButton(
                tooltip: 'Suche löschen',
                onPressed: () {
                  controller.clear();
                  onChanged('');
                },
                icon: const Icon(Icons.close),
              ),
        filled: true,
        fillColor: isDark
            ? AppColors.darkElevatedSurface
            : AppColors.careenaBubbleBackground,
        border: _border(),
        enabledBorder: _border(),
        focusedBorder: _border(color: AppColors.careenaTeal, width: 2),
      ),
    );
  }

  OutlineInputBorder _border({Color? color, double width = 0}) {
    return OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: color == null
          ? BorderSide.none
          : BorderSide(color: color, width: width),
    );
  }
}

class SettingsEmptySearchResult extends StatelessWidget {
  const SettingsEmptySearchResult({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 36),
      child: Column(
        children: [
          const Icon(Icons.search_off, size: 42, color: AppColors.careenaMuted),
          const SizedBox(height: 12),
          Text(
            'Keine passende Einstellung gefunden.',
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class SettingsLogoutAction extends StatelessWidget {
  final bool simpleView;
  final VoidCallback onPressed;

  const SettingsLogoutAction({
    super.key,
    required this.simpleView,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(18, 10, 18, 14),
        child: Center(
          heightFactor: 1,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 320),
            child: OutlinedButton.icon(
              key: const ValueKey('settings-logout-button'),
              onPressed: onPressed,
              icon: const Icon(Icons.logout),
              label: const Text('Abmelden'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.warningRed,
                side: const BorderSide(color: AppColors.warningRed),
                minimumSize: Size.fromHeight(simpleView ? 64 : 52),
                textStyle: TextStyle(
                  fontSize: simpleView ? 18 : 16,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class SettingsPrimaryButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onPressed;

  const SettingsPrimaryButton({
    super.key,
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return FilledButton.icon(
      onPressed: onPressed,
      icon: Icon(icon),
      label: Text(label),
      style: FilledButton.styleFrom(
        backgroundColor: isDark
            ? AppColors.toolbarButtonBackgroundDark
            : AppColors.toolbarButtonBackground,
        foregroundColor: isDark
            ? AppColors.toolbarButtonForegroundDark
            : AppColors.toolbarButtonForeground,
      ),
    );
  }
}
