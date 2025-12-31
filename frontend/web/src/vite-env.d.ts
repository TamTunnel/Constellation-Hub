/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_CORE_ORBITS_URL: string;
    readonly VITE_ROUTING_URL: string;
    readonly VITE_GROUND_SCHEDULER_URL: string;
    readonly VITE_AI_AGENTS_URL: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
