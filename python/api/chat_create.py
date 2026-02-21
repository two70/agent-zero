from python.helpers.api import ApiHandler, Input, Output, Request, Response


from python.helpers import projects, guids
from agent import AgentContext
from initialize import initialize_agent


class CreateChat(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        current_ctxid = input.get("current_context", "")
        new_ctxid = input.get("new_context", guids.generate_id())
        agent_profile = input.get("agent_profile", "")

        current_context = AgentContext.get(current_ctxid)

        override_settings = {}
        if agent_profile:
            from python.helpers import settings
            profile_settings = settings.get_profile_settings(agent_profile)
            override_settings["agent_profile"] = agent_profile
            if profile_settings:
                override_settings.update(profile_settings)
        
        if override_settings:
            config = initialize_agent(override_settings=override_settings)
            new_context = AgentContext(config=config, id=new_ctxid)
        else:
            new_context = self.use_context(new_ctxid)

        from python.helpers.state_monitor_integration import mark_dirty_all
        mark_dirty_all(reason="api.chat_create.CreateChat")

        return {
            "ok": True,
            "ctxid": new_context.id,
            "message": "Context created.",
        }
