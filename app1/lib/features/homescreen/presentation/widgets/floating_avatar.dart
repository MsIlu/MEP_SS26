import 'package:flutter/material.dart';

/// Animated floating avatar widget.
///
/// This widget displays a circular image
/// with a smooth vertical floating animation
/// and a soft shadow effect.
class FloatingAvatar extends StatefulWidget {
  // Path to the avatar image asset
  final String imagePath;

  const FloatingAvatar({super.key, required this.imagePath});

  @override
  State<FloatingAvatar> createState() => _FloatingAvatarState();
}

class _FloatingAvatarState extends State<FloatingAvatar>
    with SingleTickerProviderStateMixin {
  // Controls the animation loop
  late AnimationController _controller;
  // Stores the vertical movement animation
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();

    // Initialize animation controller
    _controller = AnimationController(
      vsync: this,
      // Duration of one animation cycle
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _animation = Tween<double>(
      begin: -2,
      end: 3,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, _animation.value),
          child: child,
        );
      },
      child: Container(
        height: 100,
        width: 100,
        decoration: BoxDecoration(
          color: const Color(0xFFE7F5F3),
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.14),
              blurRadius: 24,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: ClipOval(
          child: Image.asset(widget.imagePath, fit: BoxFit.cover),
        ),
      ),
    );
  }
}
