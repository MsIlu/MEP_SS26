import 'package:flutter/material.dart';
import '../../data/home_feature.dart';
import 'function_menu_tile.dart';

/// Scrollable list of home-screen feature actions.
class HomeFunctionList extends StatelessWidget {
  /// Features rendered below the list heading.
  final List<HomeFeature> features;

  const HomeFunctionList({super.key, required this.features});

  @override
  Widget build(BuildContext context) {
    // Match the page's compact padding so list rows align with the header and
    // search field across narrow and regular phone widths.
    final horizontalPadding = MediaQuery.sizeOf(context).width < 360
        ? 16.0
        : 20.0;

    return Expanded(
      child: ListView.separated(
        padding: EdgeInsets.fromLTRB(
          horizontalPadding,
          0,
          horizontalPadding,
          12,
        ),
        itemCount: features.length + 1,
        separatorBuilder: (context, index) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          // The heading is part of the same ListView so it scrolls naturally
          // with the feature rows on short screens.
          if (index == 0) {
            return const Text(
              "Deine Funktionen...",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            );
          }

          final feature = features[index - 1];

          return FunctionMenuTile(
            icon: feature.icon,
            title: feature.title,
            bgColor: feature.backgroundColor,
            onTap: feature.onTap,
          );
        },
      ),
    );
  }
}
