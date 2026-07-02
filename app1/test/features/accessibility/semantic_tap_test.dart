import 'dart:ui' show SemanticsAction, SemanticsActionEvent;

import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:app1/features/appointmentscreen/presentation/widgets/appointment_tile.dart';
import 'package:app1/features/documents/data/models/document_entry.dart';
import 'package:app1/features/documents/presentation/widgets/document_list_item.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('semantic tap triggers an icon action wrapper', (tester) async {
    var wasEdited = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AppointmentTile(
            appointment: Appointment(
              id: 'appointment-1',
              doctorName: 'Hausarzt',
              appointmentDate: DateTime(2026, 6, 30, 10),
              note: '',
            ),
            onDelete: () {},
            onEdit: () {
              wasEdited = true;
            },
          ),
        ),
      ),
    );

    final semantics = tester.ensureSemantics();

    final node = tester.getSemantics(
      find.bySemanticsLabel('Termin Hausarzt bearbeiten'),
    );

    tester.binding.performSemanticsAction(
      SemanticsActionEvent(
        type: SemanticsAction.tap,
        viewId: tester.view.viewId,
        nodeId: node.id,
      ),
    );

    semantics.dispose();

    expect(wasEdited, isTrue);
  });

  testWidgets('semantic tap opens a popup menu action wrapper', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Center(
            child: DocumentListItem(
              document: DocumentEntry(
                id: 'document-1',
                name: 'Befund.pdf',
                category: DocumentCategory.findings,
                createdAt: DateTime(2026, 6, 30),
                sizeInBytes: 2400,
                source: DocumentSource.uploaded,
              ),
              onAction: (_) {},
            ),
          ),
        ),
      ),
    );

    final semantics = tester.ensureSemantics();

    final node = tester.getSemantics(
      find.bySemanticsLabel('Dokument Befund.pdf verwalten'),
    );

    tester.binding.performSemanticsAction(
      SemanticsActionEvent(
        type: SemanticsAction.tap,
        viewId: tester.view.viewId,
        nodeId: node.id,
      ),
    );
    await tester.pumpAndSettle();

    semantics.dispose();

    expect(find.text('Anzeigen'), findsOneWidget);
    expect(find.text('Umbenennen'), findsOneWidget);
    expect(find.text('Löschen'), findsOneWidget);
  });
}
