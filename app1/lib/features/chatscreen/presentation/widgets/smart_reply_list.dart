import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

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

    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final containerColor = isDarkMode
        ? AppColors.smartReplySurfaceDark
        : AppColors.careenaNoteBackground;

    final chipColor = isDarkMode
        ? AppColors.smartReplyChipDark
        : AppColors.careenaBubbleBackground;

    final borderColor = isDarkMode
        ? AppColors.smartReplyBorderDark
        : AppColors.careenaTeal;

    final textColor = isDarkMode
        ? AppColors.careenaNoteBackground
        : AppColors.careenaDark;

    final mutedIconColor = isDarkMode
        ? AppColors.smartReplyMutedTextDark
        : AppColors.careenaDark.withValues(alpha: expanded ? 1 : 0.5);

    return Align(
      alignment: Alignment.centerRight,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        child: IntrinsicWidth(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: containerColor,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: borderColor.withValues(alpha: isDarkMode ? 0.35 : 0.15),
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
                      Text(
                        'Vorschläge',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: textColor,
                        ),
                      ),
                      const SizedBox(width: 4),
                      Icon(
                        Icons.expand_more,
                        size: 20,
                        color: mutedIconColor.withValues(
                          alpha: expanded ? 1 : 0.5,
                        ),
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
                          style: TextStyle(fontSize: 13, color: textColor),
                        ),
                        onPressed: () => widget.onSelected(reply),
                        backgroundColor: chipColor,
                        side: BorderSide(color: borderColor),
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
