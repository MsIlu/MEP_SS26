import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

/// Circular Careena avatar with an optional floating animation.
class FloatingAvatar extends StatefulWidget {
  /// Path to the avatar image asset.
  final String imagePath;

  /// Diameter of the circular avatar.
  final double size;

  const FloatingAvatar({super.key, required this.imagePath, this.size = 100});

  @override
  State<FloatingAvatar> createState() => _FloatingAvatarState();
}

class _FloatingAvatarState extends State<FloatingAvatar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _animation = Tween<double>(
      begin: -2,
      end: 3,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (MediaQuery.disableAnimationsOf(context)) {
      _controller.stop();
    } else if (!_controller.isAnimating) {
      _controller.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final avatar = _buildAvatar();

    if (MediaQuery.disableAnimationsOf(context)) {
      return avatar;
    }

    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, _animation.value),
          child: child,
        );
      },
      child: avatar,
    );
  }

  Widget _buildAvatar() {
    return Container(
      height: widget.size,
      width: widget.size,
      decoration: BoxDecoration(
        color: AppColors.careenaBubbleBackground,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.14),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: ClipOval(child: Image.asset(widget.imagePath, fit: BoxFit.cover)),
    );
  }
}
