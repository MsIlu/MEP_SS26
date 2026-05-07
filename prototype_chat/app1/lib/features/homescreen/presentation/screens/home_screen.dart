import 'package:flutter/material.dart';
import 'package:app1/features/chat/controllers/chat_controller.dart';
import '../../../chat/presentation/themes/app_colors.dart';

import '../widgets/home_header.dart';
import '../../../homescreen/presentation/widgets/home_search_bar.dart';
import '../widgets/feature_grid.dart';

class HomeScreen extends StatelessWidget {
  final ChatController controller;

  const HomeScreen({
    super.key,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,

      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              HomeHeader(
                floatingAvatar: Image.asset(
                  'images/careena_doctor.png',
                  height: 80,
                  width: 80,
                ),
              ),

              const SizedBox(height: 28),

              const HomeSearchBar(),

              const SizedBox(height: 25),

              Expanded(
                child: FeatureGrid(
                  controller: controller,
                ),
              ),
            ],
          ),
        ),
      ),

      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.textSecondary,
        backgroundColor: AppColors.card,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: "Start",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history),
            label: "Verlauf",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: "Profil",
          ),
        ],
      ),
    );
  }
}