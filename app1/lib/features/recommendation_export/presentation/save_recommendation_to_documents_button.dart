import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/features/documents/data/document_repository.dart';
import 'package:app1/features/documents/data/models/document_entry.dart';
import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/features/profiles/domain/models/profile.dart';
import '../data/recommendation_pdf_service.dart';
import 'package:flutter/material.dart';

class SaveRecommendationToDocumentsButton extends StatefulWidget {
  final String title;
  final String patientSummary;
  final String recommendation;
  final String nextSteps;
  final List<String> symptoms;
  final List<String> userMessages;
  final bool alreadySaved;
  final DateTime? recommendationCreatedAt;
  final Future<void> Function()? onSaved;

  /// Profile the recommendation belongs to (resolved by the backend session).
  /// Null means no profile was bound to the session — the document is stored
  /// without a profile association instead of falling back to the active profile.
  final int? profileId;

  const SaveRecommendationToDocumentsButton({
    super.key,
    required this.title,
    required this.patientSummary,
    required this.recommendation,
    required this.nextSteps,
    required this.symptoms,
    required this.userMessages,
    this.alreadySaved = false,
    this.recommendationCreatedAt,
    this.onSaved,
    this.profileId,
  });

  @override
  State<SaveRecommendationToDocumentsButton> createState() =>
      _SaveRecommendationToDocumentsButtonState();
}

class _SaveRecommendationToDocumentsButtonState
    extends State<SaveRecommendationToDocumentsButton> {
  final DocumentRepository _repository = DocumentRepository.instance;
  bool _isSaving = false;
  bool _savedLocally = false;

  bool _isSavedForCurrentRecommendation() {
    final recommendationCreatedAt = widget.recommendationCreatedAt;
    if (recommendationCreatedAt == null) return false;
    final key = recommendationCreatedAt.toUtc().millisecondsSinceEpoch;
    return _repository.documents.value.any(
      (document) =>
          document.profileId == widget.profileId &&
          document.source == DocumentSource.careena &&
          document.createdAt.toUtc().millisecondsSinceEpoch == key,
    );
  }

  String get _documentName {
    final title = widget.title.trim();

    if (title.toLowerCase().endsWith('.pdf')) {
      return title;
    }

    return '$title.pdf';
  }

  @override
  void initState() {
    super.initState();
    _repository.documents.addListener(_repositoryChanged);
  }

  @override
  void dispose() {
    _repository.documents.removeListener(_repositoryChanged);
    super.dispose();
  }

  void _repositoryChanged() {
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final isSaved =
        widget.alreadySaved ||
        _savedLocally ||
        _isSavedForCurrentRecommendation();

    return Tooltip(
      message: isSaved ? 'In Dokumenten gespeichert' : 'In Dokumente speichern',
      child: OutlinedButton.icon(
        onPressed: isSaved || _isSaving ? null : _saveRecommendation,
        icon: _isSaving
            ? const SizedBox.square(
                dimension: 18,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Icon(
                isSaved
                    ? Icons.check_circle_outline
                    : Icons.folder_copy_outlined,
              ),
        label: Text(isSaved ? 'Gespeichert' : 'Dokument speichern'),
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.careenaTeal,
          side: BorderSide(
            color: isSaved
                ? AppColors.careenaTeal.withValues(alpha: 0.45)
                : AppColors.careenaTeal,
          ),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
        ),
      ),
    );
  }

  Future<void> _saveRecommendation() async {
    setState(() => _isSaving = true);
    var documentStored = false;
    try {
      final dependencies = AppDependenciesScope.maybeOf(context);
      final profileApiService = dependencies?.profileApiService;
      final resolvedProfileId = widget.profileId;

      Profile? profile;

      if (resolvedProfileId != null && profileApiService != null) {
        try {
          profile = await profileApiService.getProfile(resolvedProfileId);
        } catch (_) {
          profile = null;
        }
      }

      final pdfBytes = await RecommendationPdfService().buildRecommendationPdf(
        title: widget.title,
        patientSummary: widget.patientSummary,
        recommendation: widget.recommendation,
        nextSteps: widget.nextSteps,
        symptoms: widget.symptoms,
        userMessages: widget.userMessages,
        profile: profile,
      );

      final wasAdded = await _repository.addRecommendationIfMissing(
        DocumentEntry(
          id: DateTime.now().microsecondsSinceEpoch.toString(),
          profileId: resolvedProfileId,
          name: _documentName,
          category: DocumentCategory.recommendations,
          createdAt: widget.recommendationCreatedAt ?? DateTime.now(),
          sizeInBytes: pdfBytes.lengthInBytes,
          source: DocumentSource.careena,
          fileBytes: pdfBytes,
          mimeType: 'application/pdf',
        ),
      );
      documentStored = true;

      if (mounted) {
        setState(() => _savedLocally = true);
      }

      await widget.onSaved?.call();

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppColors.careenaTeal,
          content: Text(
            wasAdded
                ? 'Handlungsempfehlung gespeichert'
                : 'Handlungsempfehlung bereits vorhanden',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ),
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            documentStored
                ? 'Dokument gespeichert, aber der Chatstatus konnte nicht aktualisiert werden'
                : 'Dokument konnte nicht gespeichert werden',
          ),
        ),
      );
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }
}
