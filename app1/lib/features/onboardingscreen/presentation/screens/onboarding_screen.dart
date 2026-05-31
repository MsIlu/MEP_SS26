import 'package:flutter/material.dart';
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
child: SingleChildScrollView(
child: Padding(
padding: const EdgeInsets.symmetric(vertical: 12),

child: Column(
children: [

const OnboardingHeader(),

const SizedBox(height: 10),


OnboardingHeroCard(
onPressed: () {
Navigator.push(
context,
MaterialPageRoute(
builder: (context) =>
ChatScreen(controller: chatController),
),
);
},
),

const SizedBox(height: 24),
Padding(
padding: const EdgeInsets.symmetric(horizontal: 22),
child: Column(
children: [

AuthButton(
text: "Anmelden",
onPressed: () {
Navigator.push(
context,
MaterialPageRoute(
builder: (context) =>
HomeScreen(controller: chatController),
),
);
},
),

const SizedBox(height: 16),
  Row(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      SizedBox(
        width:
        120,
        child: Divider(
          color: Colors.grey.shade500,
          thickness:
          1,
        ),
      ),
      const Padding(
        padding: EdgeInsets.symmetric(horizontal: 12),
        child: Text("oder", style: TextStyle(fontSize: 14)),
      ),


      SizedBox(
        width:
        120,
        child: Divider(
          color: Colors.grey.shade500,
          thickness: 1,
        ),
      ),
    ],
  ),
  const SizedBox(height: 16),


  AuthButton(
    text: "Registrieren",
    onPressed: () {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) =>
              HomeScreen(controller: chatController),
        ),
      );
    },
  ),
],
),
),

  const SizedBox(height: 10),
],
),
),
),
),
);
}
}