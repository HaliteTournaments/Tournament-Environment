//
// Created by David Li on 7/17/17.
// Modified for HaliteTournaments on 28/07/18 by Splinter
//

/*
The comments next to the constants are the orginal values,
in order to test this you need to build the halite environment
youself, check : https://github.com/HaliteChallenge/Halite-II
to know how to build the enviroment.
*/

#ifndef ENVIRONMENT_CONSTANTS_HPP
#define ENVIRONMENT_CONSTANTS_HPP

#include "json.hpp"

namespace hlt {
    constexpr auto MAX_PLAYERS = 2; //4
    constexpr auto MAX_QUEUED_MOVES = 1;

    struct GameConstants {
        int SHIPS_PER_PLAYER = 5; //3
        int PLANETS_PER_PLAYER = 6; //6
        unsigned int EXTRA_PLANETS = 6; //4
        unsigned int MAX_TURNS = 320; //300

        double DRAG = 10.0;
        double MAX_SPEED = 7.0;
        double MAX_ACCELERATION = 7.0;

        double SHIP_RADIUS = 0.5; //0.5

        unsigned short MAX_SHIP_HEALTH = 255; //255
        unsigned short BASE_SHIP_HEALTH = 255; //255
        unsigned short DOCKED_SHIP_REGENERATION = 1; //0

        unsigned int WEAPON_COOLDOWN = 1.5; //1
        double WEAPON_RADIUS = 4.0; //5.0
        int WEAPON_DAMAGE = 80; //64
        double EXPLOSION_RADIUS = 25.0; //10.0

        double DOCK_RADIUS = 4.5; //4.0
        unsigned int DOCK_TURNS = 6; //5
        int RESOURCES_PER_RADIUS = 180; //144
        bool INFINITE_RESOURCES = false; //true
        int PRODUCTION_PER_SHIP = 82; //72
        unsigned int BASE_PRODUCTIVITY = 6;
        unsigned int ADDITIONAL_PRODUCTIVITY = 6;

        int SPAWN_RADIUS = 3; //2

        static auto get_mut() -> GameConstants& {
            // Guaranteed initialized only once by C++11
            static GameConstants instance;
            return instance;
        }

        static auto get() -> const GameConstants& {
            return get_mut();
        }

        auto to_json() const -> nlohmann::json;
        auto from_json(const nlohmann::json& json) -> void;
    };
}

#endif //ENVIRONMENT_CONSTANTS_HPP
