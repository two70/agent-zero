from python.helpers.api import ApiHandler, Input, Output, Request, Response
from agent import AgentContext
from python.helpers import persist_chat
from initialize import initialize_agent


class SetAgentProfile(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        ctxid = input.get("context", "")
        profile = input.get("profile", "")
        
        if not profile:
            return Response('{"error": "Profile is required"}', status=400, mimetype="application/json")
        
        context = AgentContext.get(ctxid)
        if not context:
            return Response('{"error": "Context not found"}', status=404, mimetype="application/json")
        
        from python.helpers import settings
        profile_settings = settings.get_profile_settings(profile)
        
        override_settings = {"agent_profile": profile}
        if profile_settings:
            override_settings.update(profile_settings)
        
        new_config = initialize_agent(override_settings=override_settings)
        
        context.data["agent_profile"] = profile
        context.output_data["agent_profile"] = profile
        context.config = new_config
        context.agent0.config = new_config
        
        persist_chat.save_tmp_chat(context)
        
        from python.helpers.state_monitor_integration import mark_dirty_all
        mark_dirty_all(reason="api.chat_set_agent_profile.SetAgentProfile")
        
        return {
            "message": f"Agent profile set to '{profile}'",
            "profile": profile,
        }
