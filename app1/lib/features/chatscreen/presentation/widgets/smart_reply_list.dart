import 'package:flutter/material.dart';

/// Horizontal wrapping list of suggested next user messages.
class SmartReplyList extends StatelessWidget {
  /// Suggestions generated from the latest assistant response.
  final List<String> replies;

  /// Called with the selected suggestion text.
  final ValueChanged<String> onSelected;

  const SmartReplyList({
    super.key,
    required this.replies,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    if (replies.isEmpty) {
      // Keep the widget cheap and layout-neutral when no suggestions exist.
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      child: Center(
        child: Wrap(
          alignment: WrapAlignment.center,
          spacing: 8,
          runSpacing: 6,
          children: [
            for (final reply in replies)
              ActionChip(
                label: Text(reply),
                onPressed: () => onSelected(reply),
                backgroundColor: Colors.white,
                side: const BorderSide(color: Color(0xFF26A69A)),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
