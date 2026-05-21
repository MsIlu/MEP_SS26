import 'package:flutter/material.dart';
import '../../data/home_feature.dart';
import 'function_menu_tile.dart';

class HomeFunctionList extends StatelessWidget {
  final List<HomeFeature> features;

  const HomeFunctionList({super.key, required this.features});

  @override
  Widget build(BuildContext context) {
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
