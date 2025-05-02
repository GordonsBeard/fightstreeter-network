import { lazy } from "react";

const ClubRosterPage = lazy(() => import('../pages/ClubRosterPage'));
const LeaderBoardsPage = lazy(() => import('../pages/LeaderBoardsPage'));
const PlayerDashPage = lazy(() => import('../pages/PlayerDashPage'));
const NoRoutePage = lazy(() => import('../pages/NoRoutePage'));

export const ROUTES = [
    {
        path: "/",
        element: <ClubRosterPage />,
    },
    {
        path: "/roster",
        element: <ClubRosterPage />,
    },
    {
        path: "/leaderboards",
        element: <LeaderBoardsPage />,
    },
    {
        path: "/player/:playerId",
        element: <PlayerDashPage />,
    },
    {
        path: "*",
        element: <NoRoutePage />,
    }
];