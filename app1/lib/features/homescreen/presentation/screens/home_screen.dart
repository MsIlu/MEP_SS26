import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_screen.dart';
import 'package:flutter/material.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../data/home_feature.dart';
import '../widgets/careena_hero_card.dart';
import '../widgets/custom_bottom_nav.dart';
import '../widgets/home_function_list.dart';
import '../widgets/notification_badge_icon.dart';

/// Dashboard-style home screen with the Careena entry point and feature list.
class HomeScreen extends StatelessWidget {
  /// Shared chat controller reused when opening the chat from the home screen.
  final ChatController controller;

  const HomeScreen({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    final features = _buildFeatures();
    // A very small width needs tighter horizontal spacing than the shared
    // breakpoint helpers, because this screen has several fixed-size elements.
    final isCompact = MediaQuery.sizeOf(context).width < 360;

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 720,
          child: Column(
            children: [
              _buildHeader(isCompact),
              CareenaHeroCard(onTap: () => _navigateToChat(context)),
              _buildSearchBar(isCompact),
              HomeFunctionList(features: features),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const CustomBottomNav(),
    );
  }

  /// Navigates to the chat while preserving the existing controller instance.
  void _navigateToChat(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatScreen(controller: controller),
      ),
    );
  }

  /// Builds the top row with greeting text and notification badge.
  Widget _buildHeader(bool isCompact) {
    return Padding(
      padding: EdgeInsets.fromLTRB(
        isCompact ? 16 : 20,
        20,
        isCompact ? 16 : 20,
        10,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Text(
              "Willkommen!",
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: isCompact ? 24 : 28,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF2C5358),
              ),
            ),
          ),
          const SizedBox(width: 12),
          const NotificationBadgeIcon(count: 3),
        ],
      ),
    );
  }

  /// Builds the local search field shown below the hero card.
  Widget _buildSearchBar(bool isCompact) {
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: isCompact ? 16 : 20,
        vertical: 15,
      ),
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

  /// Defines the currently available home features.
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
        icon: Icons.medication,
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
