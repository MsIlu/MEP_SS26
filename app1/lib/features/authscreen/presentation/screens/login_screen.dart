import 'package:flutter/material.dart';

import '../../../chatscreen/controllers/chat_controller.dart';
import '../../../homescreen/presentation/screens/home_screen.dart';
import '../theme/auth_theme.dart';
import '../widgets/common/auth_buttons.dart';
import '../widgets/common/auth_fields.dart';
import '../widgets/common/auth_layout.dart';
import 'registration_screen.dart';
import '../../../../core/themes/theme_controller.dart';
import '../../state/auth_session.dart';
import '../../data/auth_api_service.dart';

/// Login flow for returning users.
class LoginScreen extends StatefulWidget {
  final ChatController chatController;
  final ThemeController themeController;
  final AuthSession authSession;
  final AuthApiService authApiService;

  const LoginScreen({
    super.key,
    required this.chatController,
    required this.themeController,
    required this.authSession,
    required this.authApiService,
  });

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  bool _isSubmitting = false;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AuthPageScaffold(
      maxWidth: AuthTheme.loginMaxWidth,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AuthTopBar(
            onBack: () => Navigator.of(context).pop(),
            onToggleTheme: widget.themeController.toggleTheme,
            isDarkMode: widget.themeController.isDarkMode,
          ),
          const SizedBox(height: 26),
          const AuthIntro(
            title: 'Willkommen zurück!',
            subtitle:
                'Melde dich an, um deine Daten einzusehen und personalisierte Unterstützung zu erhalten.',
          ),
          const SizedBox(height: 32),
          AuthTextField(
            controller: _emailController,
            label: 'E-Mail-Adresse',
            hint: 'name@beispiel.de',
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.next,
          ),
          const SizedBox(height: 18),
          AuthTextField(
            controller: _passwordController,
            label: 'Passwort',
            hint: 'Passwort eingeben',
            obscureText: _obscurePassword,
            textInputAction: TextInputAction.done,
            suffixIcon: PasswordVisibilityButton(
              obscurePassword: _obscurePassword,
              onPressed: _togglePasswordVisibility,
            ),
            onFieldSubmitted: (_) => _login(),
          ),
          const SizedBox(height: 28),
          CareenaButton(
            text: _isSubmitting ? 'Anmeldung läuft...' : 'Anmelden',
            onPressed: _isSubmitting ? null : _login,
          ),
          if (_errorMessage != null) ...[
            const SizedBox(height: 12),
            Text(
              _errorMessage!,
              style: TextStyle(
                color: Theme.of(context).colorScheme.error,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
          const SizedBox(height: 16),
          TextButton(
            // TODO(backend): Connect password reset flow once email delivery is available.
            onPressed: () {},
            child: const Text('Passwort vergessen?'),
          ),
          const SizedBox(height: 12),
          SwitchAuthMode(
            label: 'Noch kein Konto?',
            actionText: 'Registrieren',
            onPressed: _openRegistration,
          ),
        ],
      ),
    );
  }

  void _togglePasswordVisibility() {
    setState(() => _obscurePassword = !_obscurePassword);
  }

  void _openRegistration() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => RegistrationScreen(
          chatController: widget.chatController,
          themeController: widget.themeController,
          authSession: widget.authSession,
          authApiService: widget.authApiService,
        ),
      ),
    );
  }

  Future<void> _login() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    if (email.isEmpty || password.isEmpty) {
      setState(() {
        _errorMessage = 'Bitte E-Mail-Adresse und Passwort eingeben.';
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final authResponse = await widget.authApiService.login(
        email: email,
        password: password,
      );

      widget.authSession.setAuthResponse(authResponse);

      if (!mounted) return;

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) => HomeScreen(
            controller: widget.chatController,
            themeController: widget.themeController,
          ),
        ),
      );
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _errorMessage =
        'Anmeldung fehlgeschlagen. Bitte überprüfe deine Eingaben.';
      });
    } finally {
      if (!mounted) return;

      setState(() {
        _isSubmitting = false;
      });
    }
  }
}
