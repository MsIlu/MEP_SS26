import 'package:flutter/material.dart';
import '../../data/home_feature.dart';
import 'function_menu_tile.dart';

/// Scrollable list of home-screen feature actions.
class HomeFunctionList extends StatelessWidget {
  /// Features rendered below the list heading.
  final List<HomeFeature> features;
  final bool isSimpleView;
  final Key? guideTargetKey;

  const HomeFunctionList({
    super.key,
    required this.features,
    this.isSimpleView = false,
    this.guideTargetKey,
  });

  @override
  Widget build(BuildContext context) {
    // Match the page's compact padding so list rows align with the header and
    // search field across narrow and regular phone widths.
    final horizontalPadding = MediaQuery.sizeOf(context).width < 360
        ? 16.0
        : 20.0;

    return ListView.separated(
      key: guideTargetKey,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: EdgeInsets.fromLTRB(horizontalPadding, 0, horizontalPadding, 12),
      itemCount: features.length + 1,
      separatorBuilder: (context, index) =>
          SizedBox(height: isSimpleView ? 14 : 8),
      itemBuilder: (context, index) {
        if (index == 0) {
          return Text(
            isSimpleView ? "Was möchtest du tun?" : "Deine Funktionen...",
            style: TextStyle(
              fontSize: isSimpleView ? 20 : 16,
              fontWeight: FontWeight.bold,
            ),
          );
        }

        final feature = features[index - 1];

        return FunctionMenuTile(
          icon: feature.icon,
          title: feature.title,
          bgColor: feature.backgroundColor,
          onTap: feature.onTap,
          isSimpleView: isSimpleView,
          badgeCount: feature.badgeCount,
        );
      },
    );
  }
}
