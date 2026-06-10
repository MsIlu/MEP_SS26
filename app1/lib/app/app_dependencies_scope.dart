import 'package:flutter/widgets.dart';
import 'app_dependencies.dart';

/// Provides access to shared app dependencies across the widget tree
class AppDependenciesScope extends InheritedWidget {
  /// Central container for controllers, APIs, and services
  final AppDependencies dependencies;

  /// Wraps the app and exposes dependencies to all child widgets
  const AppDependenciesScope({
    super.key,
    required this.dependencies,
    required super.child,
  });

  /// Access point for dependencies from any widget
  static AppDependencies of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<AppDependenciesScope>();

    assert(scope != null, 'AppDependenciesScope not found in context');

    return scope!.dependencies;
  }

  /// No rebuilds needed because dependencies are static
  @override
  bool updateShouldNotify(AppDependenciesScope oldWidget) => false;
}