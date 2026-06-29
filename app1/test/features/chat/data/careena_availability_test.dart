import 'package:app1/features/chatscreen/data/models/careena_availability.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('CareenaAvailability', () {
    test('maps checking state to label, tooltip and color', () {
      expect(CareenaAvailability.checking.label, 'prüft...');
      expect(
        CareenaAvailability.checking.tooltip,
        'Careena prüft die Verbindung.',
      );
      expect(CareenaAvailability.checking.indicatorColor, Colors.grey);
    });

    test('maps online state to label, tooltip and color', () {
      expect(CareenaAvailability.online.label, 'online');
      expect(
        CareenaAvailability.online.tooltip,
        'Careena ist vollständig erreichbar.',
      );
      expect(CareenaAvailability.online.indicatorColor, Colors.green);
    });

    test('maps limited state to label, tooltip and color', () {
      expect(CareenaAvailability.limited.label, 'eingeschränkt');
      expect(
        CareenaAvailability.limited.tooltip,
        'Careena ist erreichbar, aber Antworten können aktuell verzögert oder eingeschränkt sein.',
      );
      expect(CareenaAvailability.limited.indicatorColor, Colors.amber);
    });

    test('maps offline state to label, tooltip and color', () {
      expect(CareenaAvailability.offline.label, 'offline');
      expect(
        CareenaAvailability.offline.tooltip,
        'Careena kann den Server gerade nicht erreichen.',
      );
      expect(CareenaAvailability.offline.indicatorColor, Colors.red);
    });
  });
}
