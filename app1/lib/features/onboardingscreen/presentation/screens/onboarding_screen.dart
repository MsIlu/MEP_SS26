import 'package:flutter/material.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../chat/controllers/chat_controller.dart';
import '../../../homescreen/presentation/screens/home_screen.dart';
import '../../../chat/presentation/screens/chat_screen.dart';
import '../widgets/auth_button.dart';
import '../widgets/onboarding_header.dart';
import '../widgets/onboarding_hero_card.dart';

class OnboardingScreen extends StatelessWidget {
  final ChatController chatController;

  const OnboardingScreen({super.key, required this.chatController});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFDDF1F1),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 560,
          scrollable: true,
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Builder(
            builder: (context) {
              final horizontalPadding = ResponsiveBreakpoints.isCompact(context)
                  ? 12.0
                  : 22.0;

              return Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const OnboardingHeader(),
                  const SizedBox(height: 10),
                  OnboardingHeroCard(onPressed: () => _navigateToChat(context)),
                  const SizedBox(height: 24),
                  Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: horizontalPadding,
                    ),
                    child: Column(
                      children: [
                        AuthButton(
                          text: "Anmelden",
                          onPressed: () => _navigateToHome(context),
                        ),
                        const SizedBox(height: 16),
                        const _AuthDivider(),
                        const SizedBox(height: 16),
                        AuthButton(
                          text: "Registrieren",
                          onPressed: () => _navigateToHome(context),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 10),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  void _navigateToChat(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ChatScreen(controller: chatController),
      ),
    );
  }

  void _navigateToHome(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => HomeScreen(controller: chatController),
      ),
    );
  }
}

class _AuthDivider extends StatelessWidget {
  const _AuthDivider();

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: Divider(color: Colors.grey.shade500, thickness: 1)),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 12),
          child: Text("oder", style: TextStyle(fontSize: 14)),
        ),
        Expanded(child: Divider(color: Colors.grey.shade500, thickness: 1)),
      ],
    );
  }
}