import 'package:flutter/material.dart';

class InlineSmartReplies extends StatefulWidget {
  final List<String> replies;
  final ValueChanged<String> onSelected;

  const InlineSmartReplies({
    super.key,
    required this.replies,
    required this.onSelected,
  });

  @override
  State<InlineSmartReplies> createState() => _InlineSmartRepliesState();
}

class _InlineSmartRepliesState extends State<InlineSmartReplies> {
  bool expanded = true;

  @override
  Widget build(BuildContext context) {
    if (widget.replies.isEmpty) {
      return const SizedBox.shrink();
    }

    return Align(
      alignment: Alignment.centerRight,
      child: Padding(
        padding: const EdgeInsets.only(right: 12, top: 4, bottom: 4),
        child: IntrinsicWidth(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFFF9FbFB),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: const Color(0xFF26A69A).withValues(alpha: 0.15),
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
                          color: Color(0xFF2C5358),
                        ),
                      ),
                      const SizedBox(width: 4),
                      Icon(
                        Icons.expand_more,
                        size: 20,
                        color: const Color(0xFF2C5358)
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
                        materialTapTargetSize:
                            MaterialTapTargetSize.shrinkWrap,
                        visualDensity: VisualDensity.compact,
                        label: Text(
                          reply,
                          style: const TextStyle(fontSize: 13),
                        ),
                        onPressed: () => widget.onSelected(reply),
                        backgroundColor: Colors.white,
                        side: const BorderSide(
                          color: Color(0xFF26A69A),
                        ),
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

