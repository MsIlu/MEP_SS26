import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:flutter/material.dart';

import '../../controllers/document_controller.dart';
import '../../data/models/document_entry.dart';
import '../widgets/document_empty_state.dart';
import '../widgets/document_filter_bar.dart';
import '../widgets/document_info_card.dart';
import '../widgets/document_list_item.dart';
import '../widgets/rename_document_dialog.dart';
import '../widgets/upload_document_dialog.dart';
import 'document_preview_screen.dart';
import '../../data/document_repository.dart';
import 'image_preview_screen.dart';
import '../../../authscreen/state/auth_session.dart';
import '../widgets/document_profile_filter.dart';

class DocumentsScreen extends StatefulWidget {
  final AuthSession? authSession;

  const DocumentsScreen({super.key, this.authSession});

  @override
  State<DocumentsScreen> createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> {
  late final DocumentController _controller;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _controller = DocumentController(
      profileId: widget.authSession?.activeProfileId,
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      DocumentRepository.instance.markAllAsSeen(
        widget.authSession?.activeProfileId,
      );
    });
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
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final searchFillColor = isDarkMode
        ? AppColors.darkElevatedSurface
        : AppColors.lightCard;
    final searchBorderColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.careenaBorder;
    final searchIconColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaDark;
    final searchTextColor = isDarkMode
        ? colorScheme.onSurface
        : AppColors.careenaDark;
    final searchHintColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaBody;

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
              final activeProfile = widget.authSession?.activeProfile;
              final canViewAllProfiles =
                  activeProfile?.profileType == 'self' ||
                  activeProfile?.role == 'owner';
              final hasActiveFilter =
                  _controller.searchQuery.trim().isNotEmpty ||
                  _controller.selectedCategory != null;

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const DocumentInfoCard(),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: _openUploadDialog,
                    icon: const Icon(Icons.upload_file_outlined),
                    label: const Text(
                      'Dokument hinzufügen',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    style: FilledButton.styleFrom(
                      backgroundColor: AppColors.careenaTeal,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 16,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Text(
                        'Deine Dokumente',
                        style: TextStyle(
                          color: colorScheme.onSurface,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        '${_controller.documents.length}',
                        style: TextStyle(
                          color: colorScheme.onSurfaceVariant,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  if (canViewAllProfiles) ...[
                    DocumentProfileFilter(
                      profiles: widget.authSession?.profiles ?? const [],
                      selectedProfileId: _controller.selectedProfileId,
                      showAllProfiles: _controller.isShowingAllProfiles,
                      onShowAll: _controller.showAllProfiles,
                      onProfileSelected: _controller.selectProfile,
                    ),
                    if ((widget.authSession?.profiles.length ?? 0) > 1)
                      const SizedBox(height: 14),
                  ],
                  TextField(
                    controller: _searchController,
                    style: TextStyle(color: searchTextColor),
                    onChanged: _controller.updateSearch,
                    decoration: InputDecoration(
                      hintText: 'Dokumente durchsuchen',
                      hintStyle: TextStyle(color: searchHintColor),
                      prefixIcon: Icon(Icons.search, color: searchIconColor),
                      filled: true,
                      fillColor: searchFillColor,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                        borderSide: BorderSide(color: searchBorderColor),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                        borderSide: BorderSide(color: searchBorderColor),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                        borderSide: const BorderSide(
                          color: AppColors.careenaTeal,
                          width: 2,
                        ),
                      ),
                      suffixIcon: _controller.searchQuery.isEmpty
                          ? null
                          : IconButton(
                              tooltip: 'Suche löschen',
                              onPressed: () {
                                _searchController.clear();
                                _controller.updateSearch('');
                                FocusScope.of(context).unfocus();
                              },
                              icon: Icon(Icons.close, color: searchIconColor),
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
                        ? DocumentEmptyState(hasActiveFilter: hasActiveFilter)
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
    );
  }

  Future<void> _openUploadDialog() async {
    final draft = await showDialog<UploadDocumentDraft>(
      context: context,
      builder: (context) => const UploadDocumentDialog(),
    );

    if (draft == null || !mounted) return;

    _controller.addDocument(
      name: draft.name,
      category: draft.category,
      fileBytes: draft.fileBytes,
      mimeType: draft.mimeType,
    );
    _showMessage('Dokument hinzugefügt');
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

  Future<void> _showDocumentDetails(DocumentEntry document) async {
    final fileBytes = document.fileBytes;

    if (fileBytes != null && document.mimeType == 'application/pdf') {
      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => DocumentPreviewScreen(
            documentName: document.name,
            fileBytes: fileBytes,
          ),
        ),
      );
      return;
    }
    if (fileBytes != null && document.mimeType.startsWith('image/')) {
      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ImagePreviewScreen(
            documentName: document.name,
            fileBytes: fileBytes,
          ),
        ),
      );
      return;
    }

    // Danach bleibt dein bisheriger Details-Dialog stehen.
    return showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        icon: const Icon(
          Icons.description_outlined,
          color: AppColors.careenaTeal,
          size: 36,
        ),
        title: Text(
          document.name,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
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
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.careenaTeal,
              foregroundColor: Colors.white,
            ),
            onPressed: () => Navigator.pop(context),
            child: const Text('Schließen'),
          ),
        ],
      ),
    );
  }

  Future<void> _renameDocument(DocumentEntry document) async {
    final name = await showDialog<String>(
      context: context,
      builder: (context) => RenameDocumentDialog(initialName: document.name),
    );

    if (name == null || name.isEmpty) return;
    _controller.renameDocument(document.id, name);
    _showMessage('Dokument umbenannt');
  }

  Future<void> _deleteDocument(DocumentEntry document) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        icon: const Icon(Icons.delete_outline, color: Colors.red, size: 36),
        title: const Text(
          'Dokument löschen',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        content: Text('Möchtest du „${document.name}“ wirklich löschen?'),
        actions: [
          TextButton(
            style: TextButton.styleFrom(foregroundColor: AppColors.careenaTeal),
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
    _showMessage('Dokument gelöscht');
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AppColors.careenaTeal,
        content: Text(
          message,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ),
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
