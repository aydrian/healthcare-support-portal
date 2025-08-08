import { type RouteConfig, route, index, layout } from "@react-router/dev/routes";

export default [
  layout("routes/_layout.tsx", [
    index("routes/dashboard.tsx"),
    route("login", "routes/login.tsx"),
    route("logout", "routes/logout.tsx"),
    route("patients", "routes/patients/index.tsx"),
    route("patients/:id", "routes/patients/patient.tsx"),
    route("chat", "routes/chat.tsx"),
    route("documents", "routes/documents.tsx"),
    route("settings", "routes/settings.tsx"),
  ]),
] satisfies RouteConfig;