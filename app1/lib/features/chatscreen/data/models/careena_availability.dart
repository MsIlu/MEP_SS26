import 'package:flutter/material.dart';

enum CareenaAvailabilityStatus { checking, online, limited, offline }

class CareenaAvailability {
  final CareenaAvailabilityStatus status;

  const CareenaAvailability(this.status);

  static const checking = CareenaAvailability(
    CareenaAvailabilityStatus.checking,
  );
  static const online = CareenaAvailability(CareenaAvailabilityStatus.online);
  static const limited = CareenaAvailability(CareenaAvailabilityStatus.limited);
  static const offline = CareenaAvailability(CareenaAvailabilityStatus.offline);

  String get label {
    switch (status) {
      case CareenaAvailabilityStatus.checking:
        return 'prüft...';
      case CareenaAvailabilityStatus.online:
        return 'online';
      case CareenaAvailabilityStatus.limited:
        return 'eingeschränkt';
      case CareenaAvailabilityStatus.offline:
        return 'offline';
    }
  }

  String get tooltip {
    switch (status) {
      case CareenaAvailabilityStatus.checking:
        return 'Careena prüft die Verbindung.';
      case CareenaAvailabilityStatus.online:
        return 'Careena ist vollständig erreichbar.';
      case CareenaAvailabilityStatus.limited:
        return 'Careena ist erreichbar, aber Antworten können aktuell verzögert oder eingeschränkt sein.';
      case CareenaAvailabilityStatus.offline:
        return 'Careena kann den Server gerade nicht erreichen.';
    }
  }

  Color get indicatorColor {
    switch (status) {
      case CareenaAvailabilityStatus.checking:
        return Colors.grey;
      case CareenaAvailabilityStatus.online:
        return Colors.green;
      case CareenaAvailabilityStatus.limited:
        return Colors.amber;
      case CareenaAvailabilityStatus.offline:
        return Colors.red;
    }
  }
}
