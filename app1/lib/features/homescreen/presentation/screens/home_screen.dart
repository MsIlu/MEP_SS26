import 'package:flutter/material.dart';
import 'package:app1/features/chat/controllers/chat_controller.dart';
import 'package:app1/features/chat/presentation/screens/chat_screen.dart';
import '../widgets/careena_hero_card.dart';
import '../widgets/function_menu_tile.dart';
import '../widgets/custom_bottom_nav.dart';

class HomeScreen extends StatelessWidget {
  final ChatController controller;
  const HomeScreen({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            CareenaHeroCard(onTap: () => _navigateToChat(context)),
            _buildSearchBar(),
            _buildFunctionList(),
          ],
        ),
      ),
      bottomNavigationBar: CustomBottomNav(),
    );
  }

  void _navigateToChat(BuildContext context) {
    Navigator.push(context, MaterialPageRoute(
        builder: (context) => ChatScreen(controller: controller)));
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 10),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const Text("Willkommen!", style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF2C5358))),
          _buildNotificationIcon(),
        ],
      ),
    );
  }

  //Todo: Statt statischer 3 als Benachichtigungsanzahl, Anzahl dynamisch erzeugen lassen
  Widget _buildNotificationIcon() {
    return Stack(
      children: [
        const Icon(Icons.notifications_none, size: 30, color: Color(0xFF8BB5BC)),
        Positioned(right: 0, child: CircleAvatar(radius: 7, backgroundColor: Colors.red,
            child: const Text("3", style: TextStyle(color: Colors.white, fontSize: 8))))
      ],
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
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(30), borderSide: BorderSide.none),
        ),
      ),
    );
  }

  Widget _buildFunctionList() {
    return Expanded(
      child: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        children: [
          const Text("Deine Funktionen...", style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
          const SizedBox(height: 15),
          FunctionMenuTile(icon: Icons.access_time, title: "Terminplanung", bgColor: Colors.teal[100]!, onTap: () {}),
          FunctionMenuTile(icon: Icons.link, title: "Medikamente", bgColor: Colors.teal[100]!, onTap: () {}),
          FunctionMenuTile(icon: Icons.description_outlined, title: "Dokumente", bgColor: Colors.teal[100]!, onTap: () {}),
          FunctionMenuTile(icon: Icons.health_and_safety_outlined, title: "Präventive Angebote", bgColor: Colors.teal[100]!, onTap: () {}),
          FunctionMenuTile(icon: Icons.menu_book_outlined, title: "Symptomtagebuch", bgColor: Colors.teal[100]!, onTap: () {}),
        ],
      ),
    );
  }
}