//! Bounded, deterministic task execution primitives.
//! This is not an OS security sandbox or an LLM inference engine.
use std::time::{Duration, Instant};

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Budget {
    pub max_runtime: Duration,
    pub max_output_bytes: usize,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Task {
    pub id: String,
    pub capability: String,
    pub input: String,
    pub budget: Budget,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum TaskError {
    InvalidBudget,
    PermissionDenied,
    TimedOut,
    OutputTooLarge,
}

pub trait Agent {
    fn execute(&self, input: &str) -> String;
}

pub fn run<A: Agent>(
    agent: &A,
    task: &Task,
    allowed_capabilities: &[&str],
) -> Result<String, TaskError> {
    if task.budget.max_runtime.is_zero() || task.budget.max_output_bytes == 0 {
        return Err(TaskError::InvalidBudget);
    }
    if !allowed_capabilities.contains(&task.capability.as_str()) {
        return Err(TaskError::PermissionDenied);
    }
    let start = Instant::now();
    let output = agent.execute(&task.input);
    if start.elapsed() > task.budget.max_runtime {
        return Err(TaskError::TimedOut);
    }
    if output.len() > task.budget.max_output_bytes {
        return Err(TaskError::OutputTooLarge);
    }
    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;

    struct Echo;
    impl Agent for Echo {
        fn execute(&self, input: &str) -> String {
            input.to_owned()
        }
    }

    fn task() -> Task {
        Task {
            id: "task-1".into(),
            capability: "research".into(),
            input: "hello".into(),
            budget: Budget {
                max_runtime: Duration::from_secs(1),
                max_output_bytes: 1024,
            },
        }
    }

    #[test]
    fn permits_scoped_task() {
        assert_eq!(run(&Echo, &task(), &["research"]), Ok("hello".into()));
    }

    #[test]
    fn rejects_unapproved_capability() {
        assert_eq!(
            run(&Echo, &task(), &["robot-actuate"]),
            Err(TaskError::PermissionDenied)
        );
    }

    #[test]
    fn rejects_excessive_output() {
        let mut t = task();
        t.budget.max_output_bytes = 2;
        assert_eq!(
            run(&Echo, &t, &["research"]),
            Err(TaskError::OutputTooLarge)
        );
    }

    #[test]
    fn rejects_zero_budget() {
        let mut t = task();
        t.budget.max_runtime = Duration::ZERO;
        assert_eq!(
            run(&Echo, &t, &["research"]),
            Err(TaskError::InvalidBudget)
        );
    }
}
