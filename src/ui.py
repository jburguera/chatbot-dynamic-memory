from dataclasses import dataclass
from typing import Any, Callable, List, Literal, Optional, Tuple

import gradio as gr
from gradio import ChatMessage, State

Role = Literal["user", "assistant", "system"]


History = List[ChatMessage]


def add_message(history: Optional[History], role: Role, content: str) -> History:
    history = history or []
    message = ChatMessage(role=role, content=content)
    history.append(message)
    return history


def handle_user_message(
    user_message: str,
    chat_history: Optional[History],
    agent_name: str,
) -> Tuple[str, History]: ...


def new_conversation() -> List[ChatMessage]:
    """
    Reset the chat history and titles for a new conversation.
    """
    return []


@dataclass
class Usage:
    requests: Optional[int]
    request_tokens: Optional[int]
    response_tokens: Optional[int]
    total_tokens: Optional[int]

    def to_markdown(self) -> str:
        not_available = "Not available"
        return f"""
<table style='width:100%; border-collapse:collapse;'>
  <tr><th style='text-align:left;'>Metric</th><th style='text-align:right;'>Value</th></tr>
  <tr><td>Requests</td><td style='text-align:right;'>{self.requests or not_available}</td></tr>
  <tr><td>Request tokens</td><td style='text-align:right;'>{self.request_tokens or not_available}</td></tr>
  <tr><td>Response tokens</td><td style='text-align:right;'>{self.response_tokens or not_available}</td></tr>
  <tr><td><b>Total tokens</b></td><td style='text-align:right;'><b>{self.total_tokens or not_available}</b></td></tr>
</table>
"""

    def update(self, other: "Usage") -> None:
        """Update the current usage with another Usage instance."""
        self.requests = (self.requests or 0) + (other.requests or 0)
        self.request_tokens = (self.request_tokens or 0) + (other.request_tokens or 0)
        self.response_tokens = (self.response_tokens or 0) + (
            other.response_tokens or 0
        )
        self.total_tokens = (self.total_tokens or 0) + (other.total_tokens or 0)


def create_chat_ui(
    messages: List[ChatMessage],
    handle_user_message_fn: Callable[[str, History, Any, State, State], Any],
    agent_choices: list = ["health_agent", "marketing_agent"],
    title: str = "AI Agent - Memory System Demo",
    last_usage: Usage = Usage(0, 0, 0, 0),
    total_usage: Usage = Usage(0, 0, 0, 0),
) -> gr.Blocks:
    with gr.Blocks(
        css="""
#conversation-list {
    min-height: 350px;
    max-height: 350px;
    overflow-y: auto;
}
#send-btn {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto;
    width: 120px;
    height: 48px;
    font-size: 1.1em;
}
#message-input-row {
    display: flex;
    align-items: center;
    gap: 10px;
}
.usage-table th, .usage-table td {
    padding: 0.2em 0.7em;
    border-bottom: 1px solid #e0e0e0;
}
.usage-table th {
    background: #f7f7fa;
}
"""
    ) as demo:
        gr.Markdown(f"# {title}")
        last_usage_state = gr.State(last_usage)
        total_usage_state = gr.State(total_usage)

        with gr.Row():
            with gr.Column(scale=1):
                agent_selector = gr.Dropdown(
                    choices=agent_choices,
                    value=agent_choices[0],
                    label="Select agent",
                )
                new_conv_btn = gr.Button("+ New conversation", variant="secondary")
                with gr.Tabs():
                    with gr.TabItem("Usage"):
                        usage_last_ui = gr.Markdown(
                            last_usage_state.value.to_markdown(),
                            elem_id="usage-last",
                        )
                        usage_total_ui = gr.Markdown(
                            f"<b>Total</b>" + total_usage_state.value.to_markdown(),
                            elem_id="usage-total",
                        )
                    with gr.TabItem("Agent settings"):
                        instructions_box = gr.Textbox(
                            label="Agent instructions",
                            lines=8,
                            value="",
                            elem_id="agent-instructions",
                        )
                        temperature = gr.Slider(
                            minimum=0.0,
                            maximum=2.0,
                            value=1.0,
                            step=0.01,
                            label="Temperature",
                            elem_id="openai-temperature",
                        )
                        top_p = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=1.0,
                            step=0.01,
                            label="Top-p",
                            elem_id="openai-top-p",
                        )
                        max_tokens = gr.Number(
                            label="Max tokens", value=1024, elem_id="openai-max-tokens"
                        )
                        save_instructions_btn = gr.Button(
                            "Save instructions", variant="primary"
                        )
                        save_openai_params_btn = gr.Button(
                            "Save OpenAI params", variant="secondary"
                        )
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Chat",
                    placeholder="Messages will appear here...",
                    type="messages",
                    height=500,
                    show_copy_button=True,
                    value=messages,  # type: ignore
                )
                with gr.Row(elem_id="message-input-row"):
                    msg = gr.Textbox(
                        label="Your message",
                        placeholder="Type your message here...",
                        lines=1,
                        interactive=True,
                        show_label=False,
                        autofocus=True,
                        scale=8,
                    )
                    send_btn = gr.Button(
                        "Send",
                        variant="primary",
                        size="lg",
                        scale=1,
                        elem_id="send-btn",
                    )

        def update_usage_displays(last_usage, total_usage):
            return (
                "<b>Current</b>" + last_usage.to_markdown(),
                f"<b>Total</b>" + total_usage.to_markdown(),
            )

        with gr.Row():
            msg.submit(
                handle_user_message_fn,
                inputs=[
                    msg,
                    chatbot,
                    agent_selector,
                    last_usage_state,
                    total_usage_state,
                ],
                outputs=[msg, chatbot, last_usage_state, total_usage_state],
            ).then(
                update_usage_displays,
                inputs=[last_usage_state, total_usage_state],
                outputs=[usage_last_ui, usage_total_ui],
            )

            send_btn.click(
                handle_user_message_fn,
                inputs=[
                    msg,
                    chatbot,
                    agent_selector,
                    last_usage_state,
                    total_usage_state,
                ],
                outputs=[msg, chatbot, last_usage_state, total_usage_state],
            ).then(
                update_usage_displays,
                inputs=[last_usage_state, total_usage_state],
                outputs=[usage_last_ui, usage_total_ui],
            )
            new_conv_btn.click(
                new_conversation,
                outputs=[chatbot],
                queue=False,
            )

            # Placeholder for usage and settings handlers
            def handle_save_instructions(instructions: str):
                pass  # Implement logic or pass handler later

            def handle_save_openai_params(
                temperature: float, top_p: float, max_tokens: int
            ):
                pass  # Implement logic or pass handler later

            save_instructions_btn.click(
                handle_save_instructions, inputs=[instructions_box], outputs=[]
            )
            save_openai_params_btn.click(
                handle_save_openai_params,
                inputs=[temperature, top_p, max_tokens],
                outputs=[],
            )
    return demo
