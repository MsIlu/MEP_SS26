import 'package:app1/app/app_page_store.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/app/app_navigation_fallbacks.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/core/widgets/careena_search_field.dart';
import 'package:app1/core/widgets/careena_snack_bar.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
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
  final ThemeController? themeController;

  const DocumentsScreen({super.key, this.authSession, this.themeController});

  @override
  State<DocumentsScreen> createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> {
  late final DocumentController _controller;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    AppPageStore.saveCurrentPage(AppPage.documents);
    _controller = DocumentController(
      profileId: widget.authSession?.activeProfileId,
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;

      DocumentRepository.instance.markAllAsSeen(
        widget.authSession?.activeProfileId,
      );
      _loadDocumentsForCurrentView();
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

    return Scaffold(
      appBar: CareenaPageHeader(
        title: 'Dokumente',
        onBack: () => navigateToHomeFallback(
          context,
          themeController: widget.themeController,
        ),
      ),
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
              final profiles = widget.authSession?.profiles ?? const [];

              return SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const DocumentInfoCard(),
                    const SizedBox(height: 16),
                    Semantics(
                      button: true,
                      label: 'Neues Dokument hinzufügen',
                      hint: 'Öffnet die Auswahl für Datei, Foto oder Kamera.',
                      onTap: _openUploadDialog,
                      child: ExcludeSemantics(
                        child: FilledButton.icon(
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
                    if (_controller.isLoading) ...[
                      const SizedBox(height: 10),
                      const LinearProgressIndicator(minHeight: 3),
                    ],
                    if (_controller.errorMessage != null) ...[
                      const SizedBox(height: 10),
                      Text(
                        _controller.errorMessage!,
                        style: TextStyle(
                          color: colorScheme.error,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                    const SizedBox(height: 12),
                    if (canViewAllProfiles) ...[
                      DocumentProfileFilter(
                        profiles: profiles,
                        selectedProfileId: _controller.selectedProfileId,
                        showAllProfiles: _controller.isShowingAllProfiles,
                        onShowAll: () {
                          _controller.showAllProfiles();
                          _loadDocumentsForCurrentView();
                        },
                        onProfileSelected: (profileId) {
                          _controller.selectProfile(profileId);
                        },
                      ),
                      if (profiles.length > 1) const SizedBox(height: 14),
                    ],
                    CareenaSearchField(
                      controller: _searchController,
                      hintText: 'Dokumente durchsuchen',
                      onChanged: _controller.updateSearch,
                    ),
                    const SizedBox(height: 14),
                    DocumentFilterBar(
                      selectedCategory: _controller.selectedCategory,
                      onSelected: _controller.selectCategory,
                    ),
                    const SizedBox(height: 18),
                    if (documents.isEmpty)
                      DocumentEmptyState(hasActiveFilter: hasActiveFilter)
                    else if (_controller.isShowingAllProfiles)
                      _GroupedDocumentList(
                        profiles: profiles,
                        documents: documents,
                        onAction: _handleAction,
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: documents.length,
                        separatorBuilder: (_, _) => const SizedBox(height: 10),
                        itemBuilder: (context, index) {
                          final document = documents[index];
                          return DocumentListItem(
                            document: document,
                            onAction: (action) =>
                                _handleAction(document, action),
                          );
                        },
                      ),
                  ],
                ),
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

    try {
      await _controller.addDocument(
        name: draft.name,
        category: draft.category,
        fileBytes: draft.fileBytes,
        mimeType: draft.mimeType,
      );
      _showMessage('Dokument hinzugefügt');
    } catch (_) {
      if (mounted) {
        _showMessage('Dokument konnte nicht gespeichert werden.');
      }
    }
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
            mimeType: document.mimeType,
          ),
        ),
      );
      return;
    }

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
    try {
      await _controller.renameDocument(document.id, name);
      _showMessage('Dokument umbenannt');
    } catch (_) {
      if (mounted) {
        _showMessage('Dokument konnte nicht umbenannt werden.');
      }
    }
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
    try {
      await _controller.deleteDocument(document.id);
      _showMessage('Dokument gelöscht');
    } catch (_) {
      if (mounted) {
        _showMessage('Dokument konnte nicht gelöscht werden.');
      }
    }
  }

  void _showMessage(String message) {
    showCareenaSnackBar(context, message);
  }

  Future<void> _loadDocumentsForCurrentView() async {
    if (_controller.isShowingAllProfiles) {
      final profileIds = widget.authSession?.profiles
          .map((profile) => profile.id)
          .toSet();

      if (profileIds == null) return;
      await Future.wait(profileIds.map(_controller.loadProfileDocuments));
      return;
    }

    final profileId = _controller.selectedProfileId;
    if (profileId == null) return;

    await _controller.loadProfileDocuments(profileId);
  }
}

class _GroupedDocumentList extends StatelessWidget {
  final List<AuthProfile> profiles;
  final List<DocumentEntry> documents;
  final Future<void> Function(DocumentEntry, DocumentAction) onAction;

  const _GroupedDocumentList({
    required this.profiles,
    required this.documents,
    required this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final groupedDocuments = _documentsByProfileId;
    final sections = profiles
        .where((profile) => groupedDocuments[profile.id]?.isNotEmpty == true)
        .toList();

    return Column(
      children: [
        for (var index = 0; index < sections.length; index++) ...[
          _ProfileDocumentSection(
            profile: sections[index],
            documents: groupedDocuments[sections[index].id] ?? const [],
            onAction: onAction,
          ),
          if (index < sections.length - 1) const SizedBox(height: 12),
        ],
      ],
    );
  }

  Map<int, List<DocumentEntry>> get _documentsByProfileId {
    final groupedDocuments = <int, List<DocumentEntry>>{};

    for (final document in documents) {
      final profileId = document.profileId;
      if (profileId == null) continue;

      groupedDocuments.putIfAbsent(profileId, () => []).add(document);
    }

    return groupedDocuments;
  }
}

class _ProfileDocumentSection extends StatelessWidget {
  final AuthProfile profile;
  final List<DocumentEntry> documents;
  final Future<void> Function(DocumentEntry, DocumentAction) onAction;

  const _ProfileDocumentSection({
    required this.profile,
    required this.documents,
    required this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Theme(
      data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 14),
        childrenPadding: const EdgeInsets.only(bottom: 12),
        initiallyExpanded: true,
        collapsedShape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        collapsedBackgroundColor: AppColors.careenaTeal.withValues(alpha: 0.08),
        backgroundColor: AppColors.careenaTeal.withValues(alpha: 0.08),
        title: Text(
          _profileSectionTitle(profile),
          style: TextStyle(
            color: colorScheme.onSurface,
            fontWeight: FontWeight.w800,
          ),
        ),
        subtitle: Text(
          '${documents.length} ${documents.length == 1 ? 'Dokument' : 'Dokumente'}',
        ),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(0, 8, 0, 0),
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: documents.length,
              separatorBuilder: (_, _) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final document = documents[index];

                return DocumentListItem(
                  document: document,
                  onAction: (action) => onAction(document, action),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  String _profileSectionTitle(AuthProfile profile) {
    if (profile.profileType == 'self') {
      return 'Hauptprofil';
    }

    return profile.displayName;
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