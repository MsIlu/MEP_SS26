import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../data/models/document_entry.dart';

enum DocumentAction { open, rename, delete }

class DocumentListItem extends StatelessWidget {
  final DocumentEntry document;
  final ValueChanged<DocumentAction> onAction;

  const DocumentListItem({
    super.key,
    required this.document,
    required this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      margin: EdgeInsets.zero,
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(color: colorScheme.outlineVariant),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: () => onAction(DocumentAction.open),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 14, 8, 14),
          child: Row(
            children: [
              Container(
                width: 46,
                height: 54,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: _categoryColor(
                    document.category,
                  ).withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _categoryIcon(document.category),
                  color: _categoryColor(document.category),
                  size: 28,
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            document.name,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                        ),
                        if (document.source == DocumentSource.careena)
                          const Padding(
                            padding: EdgeInsets.only(left: 8),
                            child: Tooltip(
                              message: 'Von Careena erstellt',
                              child: Icon(
                                Icons.auto_awesome_outlined,
                                size: 18,
                                color: AppColors.careenaTeal,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '${document.category.label} · ${_formatDate(document.createdAt)}'
                      '${document.sizeInBytes > 0 ? ' · ${_formatSize(document.sizeInBytes)}' : ''}',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              PopupMenuButton<DocumentAction>(
                tooltip: 'Dokumentaktionen',
                onSelected: onAction,
                itemBuilder: (context) => const [
                  PopupMenuItem(
                    value: DocumentAction.open,
                    child: ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: Icon(Icons.visibility_outlined),
                      title: Text('Öffnen'),
                    ),
                  ),
                  PopupMenuItem(
                    value: DocumentAction.rename,
                    child: ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: Icon(Icons.edit_outlined),
                      title: Text('Umbenennen'),
                    ),
                  ),
                  PopupMenuItem(
                    value: DocumentAction.delete,
                    child: ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: Icon(Icons.delete_outline, color: Colors.red),
                      title: Text('Löschen'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  static IconData _categoryIcon(DocumentCategory category) {
    return switch (category) {
      DocumentCategory.findings => Icons.assignment_outlined,
      DocumentCategory.laboratory => Icons.science_outlined,
      DocumentCategory.recommendations => Icons.health_and_safety_outlined,
      DocumentCategory.other => Icons.description_outlined,
    };
  }

  static Color _categoryColor(DocumentCategory category) {
    return switch (category) {
      DocumentCategory.findings => const Color(0xFF2474A6),
      DocumentCategory.laboratory => const Color(0xFF7B5EAD),
      DocumentCategory.recommendations => AppColors.careenaTeal,
      DocumentCategory.other => const Color(0xFF6B7280),
    };
  }

  static String _formatDate(DateTime date) {
    final day = date.day.toString().padLeft(2, '0');
    final month = date.month.toString().padLeft(2, '0');
    return '$day.$month.${date.year}';
  }

  static String _formatSize(int bytes) {
    if (bytes >= 1000000) {
      return '${(bytes / 1000000).toStringAsFixed(1)} MB';
    }
    return '${(bytes / 1000).round()} KB';
  }
}
