import 'package:flutter/material.dart';

import '../../../authscreen/domain/models/auth_response.dart';
import '../../../profiles/domain/models/profile.dart';

IconData profileIcon(String profileType) => switch (profileType) {
  'child' => Icons.child_care,
  'self' => Icons.person_outline,
  _ => Icons.people_outline,
};

String profileDescription(AuthProfile profile) {
  if (profile.profileType == 'child') {
    return 'Betreutes Profil';
  }

  if (profile.profileType == 'self') {
    return 'Eigenes Profil';
  }

  return profile.role == null ? 'Weiteres Profil' : 'Rolle: ${profile.role}';
}

String profileTypeForRelationship(String relationship) =>
    relationship == 'Kind' ? 'child' : 'other';

AuthProfile authProfileFromProfile(Profile profile) {
  return AuthProfile(
    id: profile.id,
    displayName: profile.displayName,
    profileType: profile.profileType,
    aiDisclaimerAcceptedAt: profile.aiDisclaimerAcceptedAt,
    role: profile.role,
  );
}
