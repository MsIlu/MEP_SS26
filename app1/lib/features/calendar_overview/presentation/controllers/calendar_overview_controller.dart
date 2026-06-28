import 'package:app1/features/appointmentscreen/controllers/appointment_controller.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:app1/features/calendar_overview/presentation/utils/calendar_overview_date_utils.dart';
import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/data/medication_repository.dart';
import 'package:app1/features/medication_plan/presentation/models/planned_medication_dose.dart';
import 'package:app1/features/medication_plan/presentation/utils/medication_plan_builder.dart';
import 'package:app1/features/symptom_diary/data/symptom_entry.dart';
import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:flutter/foundation.dart';

/// Owns calendar data and date selection for the overview screen.
class CalendarOverviewController extends ChangeNotifier {
  final AppointmentController appointmentController;
  final SymptomRepository symptomRepository;
  final MedicationRepository medicationRepository;
  final bool _ownsAppointmentController;

  late final DateTime today;
  late DateTime focusedMonth;
  late DateTime selectedDate;
  List<SymptomEntry> _symptoms = const [];
  List<MedicationEntry> _medications = const [];
  bool isLoading = true;

  CalendarOverviewController({
    required this.symptomRepository,
    required this.medicationRepository,
    AppointmentController? appointmentController,
    DateTime? now,
  })  : appointmentController = appointmentController ?? AppointmentController(),
        _ownsAppointmentController = appointmentController == null {
    final startDate = now ?? DateTime.now();
    today = DateTime(startDate.year, startDate.month, startDate.day);
    focusedMonth = DateTime(today.year, today.month);
    selectedDate = today;
    this.appointmentController.appointments.addListener(notifyListeners);
  }

  Future<void> loadEntries() async {
    final symptoms = await symptomRepository.loadEntries();
    final medications = await medicationRepository.loadEntries();
    _symptoms = symptoms;
    _medications = medications;
    isLoading = false;
    notifyListeners();
  }

  void shiftMonth(int delta) {
    focusedMonth = DateTime(focusedMonth.year, focusedMonth.month + delta);
    selectedDate = DateTime(focusedMonth.year, focusedMonth.month);
    notifyListeners();
  }

  void selectDate(DateTime date) {
    selectedDate = date;
    notifyListeners();
  }

  bool hasItemsForDate(DateTime date) {
    return appointmentsForDate(date).isNotEmpty ||
        symptomsForDate(date).isNotEmpty ||
        medicationsForDate(date).isNotEmpty;
  }

  List<Appointment> appointmentsForDate(DateTime date) {
    return appointmentController.appointments.value.where((appointment) {
      final appointmentDate = appointment.appointmentDate;
      return appointmentDate != null && isSameCalendarDay(appointmentDate, date);
    }).toList();
  }

  List<SymptomEntry> symptomsForDate(DateTime date) {
    return _symptoms.where((entry) => isSameCalendarDay(entry.date, date)).toList();
  }

  List<PlannedMedicationDose> medicationsForDate(DateTime date) {
    return plannedMedicationDosesForDate(_medications, date);
  }

  @override
  void dispose() {
    appointmentController.appointments.removeListener(notifyListeners);
    if (_ownsAppointmentController) {
      appointmentController.dispose();
    }
    super.dispose();
  }
}
