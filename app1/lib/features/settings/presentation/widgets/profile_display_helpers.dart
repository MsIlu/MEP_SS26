import 'package:flutter/material.dart';

import '../../../authscreen/domain/models/auth_response.dart';
import '../../../profiles/domain/models/profile.dart';

IconData profileIcon(String profileType) => switch (profileType) {
  'child' => Icons.child_care,
  'self' => Icons.person_outline,
  _ => Icons.people_outline,
};

String profileDescription(AuthProfile profile) {
  return switch (profile.profileType) {
    'child' => 'Kind',
    'family' => 'Familienmitglied',
    'other' => 'Andere betreute Person',
    'self' => 'Eigenes Profil',
    _ => 'Betreutes Profil',
  };
}

String profileTypeForRelationship(String relationship) =>
    switch (relationship) {
      'Kind' => 'child',
      'Familienmitglied' => 'family',
      _ => 'other',
    };

AuthProfile authProfileFromProfile(Profile profile) {
  return AuthProfile(
    id: profile.id,
    displayName: profile.displayName,
    profileType: profile.profileType,
    aiDisclaimerAcceptedAt: profile.aiDisclaimerAcceptedAt,
    role: profile.role,
  );
}
