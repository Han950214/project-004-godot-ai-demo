extends Control

const HEADLESS_EXIT_FRAME := 12
const RUNTIME_START_MARKER := "CODEX_GODOT_RUNTIME_START"
const RUNTIME_READY_MARKER := "CODEX_GODOT_RUNTIME_READY"

@onready var status_label: Label = $Center/Card/Content/Status

var _frame_count := 0
var _ready_marker_printed := false
var _elapsed := 0.0


func _ready() -> void:
	print(RUNTIME_START_MARKER)


func _process(delta: float) -> void:
	_frame_count += 1
	_elapsed += delta
	status_label.modulate.a = 0.82 + sin(_elapsed * 3.0) * 0.18

	if not _ready_marker_printed and _frame_count >= 3:
		_ready_marker_printed = true
		print(RUNTIME_READY_MARKER)

	if DisplayServer.get_name() == "headless" and _frame_count >= HEADLESS_EXIT_FRAME:
		get_tree().quit(0)
