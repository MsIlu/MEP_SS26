import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:app1/features/homescreen/data/home_feature.dart';

/// HomeFeature Model-Tests
///
/// Dieser Test stellt sicher, dass das Datenmodell für die Menükacheln der Startseite
/// (wie Terminplanung, Dokumente) Daten integer speichert und der Konstruktor Werte
/// korrekt zuweist. Das verhindert Fehler bei UI-Renderings durch Null-Pointer oder falsche Typen.
void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t07-home-screen
  group('HomeFeature - Datenmodell Validierung', () {
    test(
      'Konstruktor muss alle übergebenen Attribute korrekt in die Felder mappen',
      () {
        final feature = HomeFeature(
          icon: Icons.calendar_today,
          title: 'Terminplanung',
          backgroundColor: AppColors.careenaTeal,
          onTap: () {},
        );

        expect(feature.title, 'Terminplanung');
        expect(feature.icon, Icons.calendar_today);
        expect(feature.backgroundColor, AppColors.careenaTeal);
      },
    );
  });
}
