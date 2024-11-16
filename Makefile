.PHONY: evaluator scorer stop-evaluator stop-scorer

EVALUATOR_PARALLEL_NUM := 5
SCORER_PARALLEL_NUM := 5

USERNAME := (Your username)
PASSWORD := (Your password)

evaluator:
	@if ! tmux has-session -t evaluator 2>/dev/null; then \
		tmux new-session -s evaluator -d; \
	fi; \
	for i in $$(seq 1 $(EVALUATOR_PARALLEL_NUM)); do \
		tmux new-window -t evaluator:$$i -n opthub-evaluator-$$i; \
		tmux send-keys -t evaluator:$$i "opthub-runner evaluator" C-m; \
		sleep 1; \
		tmux send-keys -t evaluator:$$i "$(USERNAME)" C-m; \
		sleep 1; \
		tmux send-keys -t evaluator:$$i "$(PASSWORD)" C-m; \
	done

scorer:
	@if ! tmux has-session -t scorer 2>/dev/null; then \
		tmux new-session -s scorer -d; \
	fi; \
	for i in $$(seq 1 $(SCORER_PARALLEL_NUM)); do \
		tmux new-window -t scorer:$$i -n opthub-scorer-$$i; \
		tmux send-keys -t scorer:$$i "opthub-runner scorer" C-m; \
		sleep 1; \
		tmux send-keys -t scorer:$$i "$(USERNAME)" C-m; \
		sleep 1; \
		tmux send-keys -t scorer:$$i "$(PASSWORD)" C-m; \
	done

stop-evaluator:
	@if tmux has-session -t evaluator 2>/dev/null; then \
		tmux kill-session -t evaluator; \
		echo "Stopped all evaluators in session evaluator."; \
	else \
		echo "No session named evaluator found."; \
	fi

stop-scorer:
	@if tmux has-session -t scorer 2>/dev/null; then \
		tmux kill-session -t scorer; \
		echo "Stopped all scorers in session scorer."; \
	else \
		echo "No session named scorer found."; \
	fi
