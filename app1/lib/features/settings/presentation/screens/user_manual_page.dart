import 'package:app1/core/config/app_assets.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/features/documents/presentation/screens/document_preview_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class UserManualPage extends StatefulWidget {
  const UserManualPage({super.key});

  @override
  State<UserManualPage> createState() => _UserManualPageState();
}

class _UserManualPageState extends State<UserManualPage> {
  late final Future<Uint8List> _manualBytes = _loadManualBytes();

  Future<Uint8List> _loadManualBytes() async {
    // Keep the manual bundled with the app so settings can open it offline.
    final data = await rootBundle.load(AppAssets.userManualPdf);
    return data.buffer.asUint8List();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Uint8List>(
      future: _manualBytes,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          return DocumentPreviewScreen(
            documentName: 'Careena_Benutzerhandbuch.pdf',
            fileBytes: snapshot.data!,
          );
        }

        if (snapshot.hasError) {
          return const _UserManualErrorView();
        }

        return const _UserManualLoadingView();
      },
    );
  }
}

class _UserManualLoadingView extends StatelessWidget {
  const _UserManualLoadingView();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      appBar: CareenaPageHeader(title: 'Benutzerhandbuch'),
      body: Center(
        child: CircularProgressIndicator(color: AppColors.careenaTeal),
      ),
    );
  }
}

class _UserManualErrorView extends StatelessWidget {
  const _UserManualErrorView();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: const CareenaPageHeader(title: 'Benutzerhandbuch'),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            'Das Benutzerhandbuch konnte nicht geladen werden.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: colorScheme.onSurface,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ),
    );
  }
}
