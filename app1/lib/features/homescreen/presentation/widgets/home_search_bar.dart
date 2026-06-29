import 'package:app1/core/widgets/careena_search_field.dart';
import 'package:flutter/material.dart';

/// Search field shown below the home hero card.
class HomeSearchBar extends StatefulWidget {
  /// Whether the field should use the narrow phone spacing.
  final bool isCompact;
  final Key? guideTargetKey;

  const HomeSearchBar({
    super.key,
    required this.isCompact,
    this.guideTargetKey,
  });

  @override
  State<HomeSearchBar> createState() => _HomeSearchBarState();
}

class _HomeSearchBarState extends State<HomeSearchBar> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: widget.isCompact ? 16 : 20,
        vertical: 15,
      ),
      child: CareenaSearchField(
        fieldKey: widget.guideTargetKey,
        controller: _controller,
        hintText: 'Suchen...',
        onChanged: (_) {},
      ),
    );
  }
}
