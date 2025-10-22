from database.db import db_manager, init_db
from core.validation import email_validator
from core.schemas import LookupRequest, TaskStatus
from tasks.celery_config import app as celery_app
from tasks.worker_tasks import social_lookup_task

class CyberzillaCLI:

    async def submit_lookup_task(self, email: str, advanced: bool = False):
        """Submit email lookup task to Celery"""
        
        # Validate email first
        validation_result = await email_validator.validate_email_comprehensive(email)
        
        if not validation_result['is_valid']:
            console.print(f"[bold red]❌ Invalid email: {validation_result.get('details', {}).get('error', 'Unknown error')}[/bold red]")
            return None
        
        if validation_result['risk_score'] > 0.7:
            if not Confirm.ask(f"[bold yellow]⚠️  High-risk email detected (score: {validation_result['risk_score']:.2f}). Continue?[/bold yellow]"):
                return None
        
        # Create lookup request
        lookup_request = LookupRequest(
            email=email,
            advanced_analysis=advanced,
            collect_fingerprint=True
        )
        
        # Submit to Celery
        task = social_lookup_task.delay(
            email=email,
            advanced_analysis=advanced,
            user_context={'cli_user': self.current_user}
        )
        
        console.print(f"[bold green]✅ Task submitted: {task.id}[/bold green]")
        return task.id
class CyberzillaCLI:
    def __init__(self):
        # ... existing code ...
        self.trust_manager = EnterpriseTrustManager()
        self.resource_orchestrator = AdaptiveResourceOrchestrator()
        self.agent_generator = AgentGenerator()
        
    async def startup_sequence(self):
        """Enhanced startup with legitimacy and resource optimization"""
        console.print("[bold blue]🏢 Cyberzilla Enterprise Intelligence Platform[/bold blue]")
        console.print("[dim]Initializing enterprise-grade security and performance...[/dim]")
        
        # Establish enterprise presence
        self.trust_manager.establish_enterprise_presence()
        
        # Assess system resources
        resources = await self.resource_orchestrator.assess_system_resources()
        strategy = self.resource_orchestrator.determine_resource_strategy(resources)
        
        # Generate and optimize agents
        await self.initialize_optimized_agents(strategy)
        
        # Display legitimacy report
        await self.display_legitimacy_report()
        
        console.print("[bold green]✅ Enterprise platform initialized successfully[/bold green]")
    
    async def initialize_optimized_agents(self, strategy: ResourceStrategy):
        """Initialize agents with resource optimization"""
        console.print("[blue]🤖 Initializing AI agents with resource optimization...[/blue]")
        
        # Get optimization settings
        optimizations = await self.resource_orchestrator.optimize_agent_operations(strategy)
        
        # Initialize agents for each platform
        platforms = ['linkedin', 'github', 'twitter', 'facebook', 'instagram']
        
        for platform in platforms:
            try:
                agent = await self.agent_generator.generate_agent(platform)
                console.print(f"  ✅ {platform.title()} agent: {agent.agent_id}")
            except Exception as e:
                console.print(f"  ❌ {platform.title()} agent failed: {e}")
        
        console.print(f"[green]✅ {len(platforms)} AI agents initialized with {strategy.level.value} resource strategy[/green]")
