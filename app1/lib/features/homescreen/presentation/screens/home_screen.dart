import 'package:app1/features/chat/controllers/chat_controller.dart';
import 'package:app1/features/chat/presentation/screens/chat_screen.dart';
import 'package:flutter/material.dart';
import '../../data/home_feature.dart';
import '../widgets/careena_hero_card.dart';
import '../widgets/custom_bottom_nav.dart';
import '../widgets/home_function_list.dart';
import '../widgets/notification_badge_icon.dart';

class HomeScreen extends StatelessWidget {
  final ChatController controller;

  const HomeScreen({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    final features = _buildFeatures();

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            CareenaHeroCard(onTap: () => _navigateToChat(context)),
            _buildSearchBar(),
            HomeFunctionList(features: features),
          ],
        ),
      ),
      bottomNavigationBar: const CustomBottomNav(),
    );
  }

  void _navigateToChat(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatScreen(controller: controller),
      ),
    );
  }

  Widget _buildHeader() {
    return const Padding(
      padding: EdgeInsets.fromLTRB(20, 20, 20, 10),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            "Willkommen!",
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Color(0xFF2C5358),
            ),
          ),
          NotificationBadgeIcon(count: 3),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
      child: TextField(
        decoration: InputDecoration(
          hintText: "Suchen...",
          prefixIcon: const Icon(Icons.search),
          filled: true,
          fillColor: Colors.grey[100],
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
            borderSide: BorderSide.none,
          ),
        ),
      ),
    );
  }

  List<HomeFeature> _buildFeatures() {
    final featureColor = Colors.teal[100]!;

    return [
      HomeFeature(
        icon: Icons.access_time,
        title: "Terminplanung",
        backgroundColor: featureColor,
        onTap: () {},
      ),
      HomeFeature(
        icon: Icons.link,
        title: "Medikamente",
        backgroundColor: featureColor,
        onTap: () {},
      ),
      HomeFeature(
        icon: Icons.description_outlined,
        title: "Dokumente",
        backgroundColor: featureColor,
        onTap: () {},
      ),
      HomeFeature(
        icon: Icons.health_and_safety_outlined,
        title: "Präventive Angebote",
        backgroundColor: featureColor,
        onTap: () {},
      ),
      HomeFeature(
        icon: Icons.menu_book_outlined,
        title: "Symptomtagebuch",
        backgroundColor: featureColor,
        onTap: () {},
      ),
    ];
  }
}
