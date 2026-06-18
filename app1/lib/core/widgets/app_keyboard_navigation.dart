import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class AppKeyboardNavigation extends StatefulWidget {
  final Widget child;

  const AppKeyboardNavigation({super.key, required this.child});

  @override
  State<AppKeyboardNavigation> createState() => _AppKeyboardNavigationState();
}

class _AppKeyboardNavigationState extends State<AppKeyboardNavigation> {
  @override
  void initState() {
    super.initState();
    HardwareKeyboard.instance.addHandler(_handleKeyEvent);
  }

  @override
  void dispose() {
    HardwareKeyboard.instance.removeHandler(_handleKeyEvent);
    super.dispose();
  }

  bool _handleKeyEvent(KeyEvent event) {
    if (event is! KeyDownEvent || _hasModifierPressed()) {
      return false;
    }

    final primaryFocus = FocusManager.instance.primaryFocus;
    if (primaryFocus == null) {
      return false;
    }

    final isEditable = _isEditableFocus(primaryFocus);
    final key = event.logicalKey;

    if (key == LogicalKeyboardKey.arrowDown) {
      return _moveFocus(primaryFocus, TraversalDirection.down, forward: true);
    }

    if (key == LogicalKeyboardKey.arrowUp) {
      return _moveFocus(primaryFocus, TraversalDirection.up, forward: false);
    }

    if (!isEditable && key == LogicalKeyboardKey.arrowRight) {
      return _moveFocus(primaryFocus, TraversalDirection.right, forward: true);
    }

    if (!isEditable && key == LogicalKeyboardKey.arrowLeft) {
      return _moveFocus(primaryFocus, TraversalDirection.left, forward: false);
    }

    return false;
  }

  bool _moveFocus(
    FocusNode focusNode,
    TraversalDirection direction, {
    required bool forward,
  }) {
    final moved = focusNode.focusInDirection(direction);
    if (moved) {
      return true;
    }

    return forward ? focusNode.nextFocus() : focusNode.previousFocus();
  }

  bool _isEditableFocus(FocusNode focusNode) {
    final context = focusNode.context;
    if (context == null) {
      return false;
    }

    return context.widget is EditableText ||
        context.findAncestorWidgetOfExactType<EditableText>() != null;
  }

  bool _hasModifierPressed() {
    final keyboard = HardwareKeyboard.instance;
    return keyboard.isShiftPressed ||
        keyboard.isControlPressed ||
        keyboard.isAltPressed ||
        keyboard.isMetaPressed;
  }

  @override
  Widget build(BuildContext context) {
    return FocusTraversalGroup(
      policy: ReadingOrderTraversalPolicy(),
      child: widget.child,
    );
  }
}
