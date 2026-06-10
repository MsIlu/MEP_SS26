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

    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: isDark ? AppColors.darkElevatedSurface : Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.careenaInfoBorder, width: 1.5),
      ),
      child: Column(
        children: [
          for (var index = 0; index < children.length; index++) ...[
            children[index],
            if (index < children.length - 1)
              const Divider(height: 1, indent: 76),
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
        color: isActive ? Colors.white : AppColors.careenaDark,
      ),
    );
  }
}