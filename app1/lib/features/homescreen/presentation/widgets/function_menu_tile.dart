import 'package:flutter/material.dart';

class FunctionMenuTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final Color bgColor;
  final VoidCallback onTap;

  const FunctionMenuTile({
    super.key,
    required this.icon,
    required this.title,
    required this.bgColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[200]!),
        borderRadius: BorderRadius.circular(20),
      ),
      child: ListTile(
        onTap: onTap,
        contentPadding: const EdgeInsets.symmetric(horizontal: 15, vertical: 5),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: const Color(0xFF2C5358)),
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Color(0xFF2C5358),
          ),
        ),
        trailing: const Icon(Icons.chevron_right, color: Color(0xFF26A69A)),
      ),
    );
  }
}