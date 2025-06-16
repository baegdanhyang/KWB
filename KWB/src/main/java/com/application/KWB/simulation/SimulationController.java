package com.application.KWB.simulation;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.io.IOException;
import java.util.*;

@RestController
@RequestMapping("/simulation")
public class SimulationController {

    @Autowired
    private SimulationService simulationService;

    @PostMapping("/run")
    public Map<String, Object> runSimulation(@RequestBody Map<String, Object> rawInput) throws IOException {
        // 프론트에서 받은 선수명 리스트를 JSON 구조로 변환
        List<String> homeBatters = (List<String>) rawInput.get("homeBatters");
        List<String> homePitchers = (List<String>) rawInput.get("homePitchers");
        Map<String, Object> teamA = new HashMap<>();
        teamA.put("name", rawInput.getOrDefault("homeName", "홈팀"));
        teamA.put("lineup", homeBatters);
        teamA.put("starter", homePitchers.get(0));
        teamA.put("bullpen", homePitchers.size() > 1 ? homePitchers.subList(1, homePitchers.size()) : new ArrayList<>());

        List<String> awayBatters = (List<String>) rawInput.get("awayBatters");
        List<String> awayPitchers = (List<String>) rawInput.get("awayPitchers");
        Map<String, Object> teamB = new HashMap<>();
        teamB.put("name", rawInput.getOrDefault("awayName", "어웨이팀"));
        teamB.put("lineup", awayBatters);
        teamB.put("starter", awayPitchers.get(0));
        teamB.put("bullpen", awayPitchers.size() > 1 ? awayPitchers.subList(1, awayPitchers.size()) : new ArrayList<>());

        Map<String, Object> simInput = new HashMap<>();
        simInput.put("team_A", teamA);
        simInput.put("team_B", teamB);
        simInput.put("match_count", rawInput.getOrDefault("matchCount", 10));

      
        
        Map<String, Object> result = simulationService.runSimulation(simInput);
        System.out.println("시뮬레이션 결과: " + result);
        return result;
    }
}
