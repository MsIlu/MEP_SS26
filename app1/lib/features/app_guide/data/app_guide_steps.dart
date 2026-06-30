enum AppGuideTarget { careena, features, theme, navigation }

class AppGuideStep {
  final AppGuideTarget target;
  final String title;
  final String description;
  final double spotlightRadius;

  const AppGuideStep({
    required this.target,
    required this.title,
    required this.description,
    required this.spotlightRadius,
  });
}

const appGuideSteps = [
  AppGuideStep(
    target: AppGuideTarget.careena,
    spotlightRadius: 30,
    title: 'Careena ist für dich da',
    description:
        'Tippe auf diesen Knopf, wenn du Beschwerden beschreiben oder eine gesundheitliche Frage stellen möchtest.',
  ),
  AppGuideStep(
    target: AppGuideTarget.theme,
    spotlightRadius: 24,
    title: 'Hell oder dunkel',
    description:
        'Mit diesem Schalter oben rechts wechselst du jederzeit zwischen Hell- und Dunkelmodus.',
  ),
  AppGuideStep(
    target: AppGuideTarget.features,
    spotlightRadius: 22,
    title: 'Alles Wichtige an einem Ort',
    description:
        'Tippe auf eine Funktion, um dein Symptom- oder Medikamententagebuch, deine Termine, oder deine Dokumente zu öffnen.',
  ),
  AppGuideStep(
    target: AppGuideTarget.navigation,
    spotlightRadius: 40,
    title: 'Immer schnell erreichbar',
    description:
    'Mit dieser Leiste wechselst du jederzeit zur Startseite, zum Kalender, zu deiner Chathistorie oder zu deinen Einstellungen.',
  ),
];
