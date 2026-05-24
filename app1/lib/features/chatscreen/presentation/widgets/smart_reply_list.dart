import 'package:flutter/material.dart';
import '../themes/app_colors.dart';

/// wrapping list of suggested next user messages.
class SmartReplyList extends StatefulWidget {
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
  State<SmartReplyList> createState() => _SmartRepliesState();
}

class _SmartRepliesState extends State<SmartReplyList> {
  bool expanded = true;

  @override
  Widget build(BuildContext context) {
    if (widget.replies.isEmpty) {
      // Keep the widget cheap and layout-neutral when no suggestions exist.
      return const SizedBox.shrink();
    }

    return Align(
      alignment: Alignment.centerRight,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        child: IntrinsicWidth(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: AppColors.careenaNoteBackground,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: AppColors.careenaTeal.withValues(alpha: 0.15),
              ),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                InkWell(
                  borderRadius: BorderRadius.circular(10),
                  onTap: () {
                    setState(() {
                      expanded = !expanded;
                    });
                  },
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text(
                        'Vorschläge',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: AppColors.careenaDark,
                        ),
                      ),
                      const SizedBox(width: 4),
                      Icon(
                        Icons.expand_more,
                        size: 20,
                        color: AppColors.careenaDark
                            .withValues(alpha: expanded ? 1 : 0.5),
                      ),
                    ],
                  ),
                ),

                if (expanded) ...[
                  const SizedBox(height: 8),

                  for (final reply in widget.replies) ...[
                    Align(
                      alignment: Alignment.centerRight,
                      child: ActionChip(
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        visualDensity: VisualDensity.compact,
                        label: Text(
                          reply,
                          style: const TextStyle(fontSize: 13),
                        ),
                        onPressed: () => widget.onSelected(reply),
                        backgroundColor: Colors.white,
                        side: const BorderSide(color: AppColors.careenaTeal,),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                  ],
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

