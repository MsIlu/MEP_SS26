import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:flutter/material.dart';

import '../../controllers/document_controller.dart';
import '../../data/models/document_entry.dart';
import '../widgets/document_empty_state.dart';
import '../widgets/document_filter_bar.dart';
import '../widgets/document_list_item.dart';
import '../widgets/upload_document_dialog.dart';

class DocumentsScreen extends StatefulWidget {
  const DocumentsScreen({super.key});

  @override
  State<DocumentsScreen> createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> {
  late final DocumentController _controller;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _controller = DocumentController();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final horizontalPadding = MediaQuery.sizeOf(context).width < 360
        ? 14.0
        : 20.0;

    return Scaffold(
      appBar: const CareenaPageHeader(title: 'Dokumente'),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 900,
          padding: EdgeInsets.fromLTRB(
            horizontalPadding,
            18,
            horizontalPadding,
            16,
          ),
          child: AnimatedBuilder(
            animation: _controller,
            builder: (context, _) {
              final documents = _controller.visibleDocuments;
              final hasActiveFilter =
                  _controller.searchQuery.trim().isNotEmpty ||
                  _controller.selectedCategory != null;

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _DocumentOverviewHeader(
                    documentCount: _controller.documents.length,
                    onUpload: _openUploadDialog,
                  ),
                  const SizedBox(height: 18),
                  TextField(
                    controller: _searchController,
                    onChanged: _controller.updateSearch,
                    decoration: InputDecoration(
                      hintText: 'Dokumente durchsuchen',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _controller.searchQuery.isEmpty
                          ? null
                          : IconButton(
                              tooltip: 'Suche löschen',
                              onPressed: () {
                                _searchController.clear();
                                _controller.updateSearch('');
                                FocusScope.of(context).unfocus();
                              },
                              icon: const Icon(Icons.close),
                            ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  DocumentFilterBar(
                    selectedCategory: _controller.selectedCategory,
                    onSelected: _controller.selectCategory,
                  ),
                  const SizedBox(height: 18),
                  Expanded(
                    child: documents.isEmpty
                        ? DocumentEmptyState(
                            hasActiveFilter: hasActiveFilter,
                            onUpload: _openUploadDialog,
                          )
                        : ListView.separated(
                            itemCount: documents.length,
                            separatorBuilder: (_, _) =>
                                const SizedBox(height: 10),
                            itemBuilder: (context, index) {
                              final document = documents[index];
                              return DocumentListItem(
                                document: document,
                                onAction: (action) =>
                                    _handleAction(document, action),
                              );
                            },
                          ),
                  ),
                ],
              );
            },
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        tooltip: 'Dokument hinzufügen',
        onPressed: _openUploadDialog,
        backgroundColor: AppColors.careenaTeal,
        foregroundColor: Colors.white,
        child: const Icon(Icons.add),
      ),
    );
  }

  Future<void> _openUploadDialog() async {
    final draft = await showDialog<UploadDocumentDraft>(
      context: context,
      builder: (context) => const UploadDocumentDialog(),
    );

    if (draft == null || !mounted) return;

    _controller.addDocument(name: draft.name, category: draft.category);
    _showMessage('Dokument wurde zur Übersicht hinzugefügt.');
  }

  Future<void> _handleAction(
    DocumentEntry document,
    DocumentAction action,
  ) async {
    switch (action) {
      case DocumentAction.open:
        await _showDocumentDetails(document);
        return;
      case DocumentAction.rename:
        await _renameDocument(document);
        return;
      case DocumentAction.delete:
        await _deleteDocument(document);
        return;
    }
  }

  Future<void> _showDocumentDetails(DocumentEntry document) {
    return showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        icon: const Icon(
          Icons.description_outlined,
          color: AppColors.careenaTeal,
          size: 36,
        ),
        title: Text(document.name),
        content: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _DetailRow(label: 'Kategorie', value: document.category.label),
              _DetailRow(
                label: 'Quelle',
                value: document.source == DocumentSource.careena
                    ? 'Careena'
                    : 'Hochgeladen',
              ),
            ],
          ),
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Schließen'),
          ),
        ],
      ),
    );
  }

  Future<void> _renameDocument(DocumentEntry document) async {
    final controller = TextEditingController(text: document.name);
    final name = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Dokument umbenennen'),
        content: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: TextField(
            controller: controller,
            autofocus: true,
            maxLength: 100,
            decoration: const InputDecoration(labelText: 'Dokumentname'),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, controller.text.trim()),
            child: const Text('Speichern'),
          ),
        ],
      ),
    );
    controller.dispose();

    if (name == null || name.isEmpty) return;
    _controller.renameDocument(document.id, name);
    _showMessage('Dokument wurde umbenannt.');
  }

  Future<void> _deleteDocument(DocumentEntry document) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Dokument löschen'),
        content: Text(
          'Möchtest du „${document.name}“ wirklich aus der Übersicht löschen?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Löschen'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;
    _controller.deleteDocument(document.id);
    _showMessage('Dokument wurde gelöscht.');
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }
}

class _DocumentOverviewHeader extends StatelessWidget {
  final int documentCount;
  final VoidCallback onUpload;

  const _DocumentOverviewHeader({
    required this.documentCount,
    required this.onUpload,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 520;
        final copy = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Deine medizinischen Unterlagen',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 4),
            Text(
              '$documentCount ${documentCount == 1 ? 'Dokument' : 'Dokumente'} gespeichert',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        );

        if (compact) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              copy,
              const SizedBox(height: 14),
              FilledButton.icon(
                onPressed: onUpload,
                icon: const Icon(Icons.upload_file_outlined),
                label: const Text('Dokument hinzufügen'),
              ),
            ],
          );
        }

        return Row(
          children: [
            Expanded(child: copy),
            const SizedBox(width: 16),
            FilledButton.icon(
              onPressed: onUpload,
              icon: const Icon(Icons.upload_file_outlined),
              label: const Text('Dokument hinzufügen'),
            ),
          ],
        );
      },
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 88,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
