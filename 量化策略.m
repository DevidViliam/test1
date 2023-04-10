//
//  量化策略.m
//  okex
//
//  Created by 林 on 2023/4/10.
//

#import "量化策略.h"

@implementation ____

// 均线策略
- (NSDictionary *)movingAverageStrategy:(NSDictionary *)data shortWindow:(int)shortWindow longWindow:(int)longWindow {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *shortMAvgArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *longMAvgArray = [NSMutableArray arrayWithCapacity:data.count];
    double shortMAvg = 0, longMAvg = 0;
    for (int i = 0; i < data.count; i++) {
        double close = [data[i][@"close"] doubleValue];
        if (i >= shortWindow) {
            shortMAvg = [[signalArray subarrayWithRange:NSMakeRange(i-shortWindow, shortWindow)] valueForKeyPath:@"@avg.self"];
        } else {
            shortMAvg = close;
        }
        [shortMAvgArray addObject:@(shortMAvg)];
        
        if (i >= longWindow) {
            longMAvg = [[signalArray subarrayWithRange:NSMakeRange(i-longWindow, longWindow)] valueForKeyPath:@"@avg.self"];
        } else {
            longMAvg = close;
        }
        [longMAvgArray addObject:@(longMAvg)];
        
        if (shortMAvg > longMAvg) {
            [signalArray addObject:@(1)];
        } else {
            [signalArray addObject:@(0)];
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:shortMAvgArray forKey:@"short_mavg"];
    [signals setObject:longMAvgArray forKey:@"long_mavg"];
    return signals;
}

// 动量策略
- (NSDictionary *)momentumStrategy:(NSDictionary *)data n:(int)n {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *momentumArray = [NSMutableArray arrayWithCapacity:data.count];
    for (int i = 0; i < data.count; i++) {
        double close = [data[i][@"close"] doubleValue];
        if (i < n) {
            [momentumArray addObject:@(0)];
            [signalArray addObject:@(0)];
        } else {
            double momentum = (close - [data[i-n][@"close"] doubleValue]) / [data[i-n][@"close"] doubleValue];
            [momentumArray addObject:@(momentum)];
            if (momentum > 0) {
                [signalArray addObject:@(1)];
            } else {
                [signalArray addObject:@(0)];
            }
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:momentumArray forKey:@"momentum"];
    return signals;
}

//日内交易
- (NSDictionary *)intradayStrategy:(NSDictionary *)data {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    double prevPrice = 0;
    double prevVolume = 0;
    double longPosition = 0;
    double shortPosition = 0;
    for (int i = 0; i < data.count; i++) {
        double price = [data[i][@"close"] doubleValue];
        double volume = [data[i][@"volume"] doubleValue];
        [priceArray addObject:@(price)];
        double deltaPrice = price - prevPrice;
        double deltaVolume = volume - prevVolume;
        if (deltaPrice > 0 && deltaVolume > 0) {
            longPosition = deltaPrice * deltaVolume;
            shortPosition = 0;
            [signalArray addObject:@(1)];
        } else if (deltaPrice < 0 && deltaVolume > 0) {
            longPosition = 0;
            shortPosition = -deltaPrice * deltaVolume;
            [signalArray addObject:@(-1)];
        } else {
            longPosition = 0;
            shortPosition = 0;
            [signalArray addObject:@(0)];
        }
        prevPrice = price;
        prevVolume = volume;
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    return signals;
}

    
// 突破策略
- (NSDictionary *)breakoutStrategy:(NSDictionary *)data n:(int)n {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *highArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *lowArray = [NSMutableArray arrayWithCapacity:data.count];
    double highestHigh = 0, lowestLow = 0;
    for (int i = 0; i < data.count; i++) {
        double high = [data[i][@"high"] doubleValue];
        double low = [data[i][@"low"] doubleValue];
        if (i < n) {
            [highArray addObject:@(0)];
            [lowArray addObject:@(0)];
            [signalArray addObject:@(0)];
        } else {
            highestHigh = [[highArray subarrayWithRange:NSMakeRange(i-n, n)] valueForKeyPath:@"@max.self"];
            lowestLow = [[lowArray subarrayWithRange:NSMakeRange(i-n, n)] valueForKeyPath:@"@min.self"];
            [highArray addObject:@(high)];
            [lowArray addObject:@(low)];
            if (high > highestHigh) {
                [signalArray addObject:@(1)];
            } else if (low < lowestLow) {
                [signalArray addObject:@(-1)];
            } else {
                [signalArray addObject:@(0)];
            }
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:highArray forKey:@"highest_high"];
    [signals setObject:lowArray forKey:@"lowest_low"];
    return signals;
}

// 反转策略
- (NSDictionary *)reversalStrategy:(NSDictionary *)data n:(int)n {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *highArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *lowArray = [NSMutableArray arrayWithCapacity:data.count];
    double highestHigh = 0, lowestLow = 0;
    for (int i = 0; i < data.count; i++) {
        double high = [data[i][@"high"] doubleValue];
        double low = [data[i][@"low"] doubleValue];
        if (i < n) {
            [highArray addObject:@(0)];
            [lowArray addObject:@(0)];
            [signalArray addObject:@(0)];
        } else {
            highestHigh = [[highArray subarrayWithRange:NSMakeRange(i-n, n)] valueForKeyPath:@"@max.self"];
            lowestLow = [[lowArray subarrayWithRange:NSMakeRange(i-n, n)] valueForKeyPath:@"@min.self"];
            [highArray addObject:@(high)];
            [lowArray addObject:@(low)];
            if (high > highestHigh) {
                [signalArray addObject:@(-1)];
            } else if (low < lowestLow) {
                [signalArray addObject:@(1)];
            } else {
                [signalArray addObject:@(0)];
            }
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:highArray forKey:@"highest_high"];
    [signals setObject:lowArray forKey:@"lowest_low"];
    return signals;
}

// 套利策略
- (NSDictionary *)arbitrageStrategy:(NSDictionary *)data1 data2:(NSDictionary *)data2 {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data1.count];
    NSMutableArray *price1Array = [NSMutableArray arrayWithCapacity:data1.count];
    NSMutableArray *price2Array = [NSMutableArray arrayWithCapacity:data1.count];
    double prevPrice1 = 0;
    double prevPrice2 = 0;
    double longPosition = 0;
    double shortPosition = 0;
    for (int i = 0; i < data1.count; i++) {
        double price1 = [data1[i][@"close"] doubleValue];
        double price2 = [data2[i][@"close"] doubleValue];
        [price1Array addObject:@(price1)];
        [price2Array addObject:@(price2)];
        double deltaPrice1 = price1 - prevPrice1;
        double deltaPrice2 = price2 - prevPrice2;
        double spread = price1 - price2;
        if (deltaPrice1 > 0 && deltaPrice2 < 0 && spread > 0) {
            longPosition = spread;
            shortPosition = 0;
            [signalArray addObject:@(1)];
        } else if (deltaPrice1 < 0 && deltaPrice2 > 0 && spread < 0) {
            longPosition = 0;
            shortPosition = -spread;
            [signalArray addObject:@(-1)];
        } else {
            longPosition = 0;
            shortPosition = 0;
            [signalArray addObject:@(0)];
        }
        prevPrice1 = price1;
        prevPrice2 = price2;
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:price1Array forKey:@"price1"];
    [signals setObject:price2Array forKey:@"price2"];
    return signals;
}


// 多空策略
- (NSDictionary *)longShortStrategy:(NSDictionary *)data shortWindow:(int)shortWindow longWindow:(int)longWindow {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *shortMAvgArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *longMAvgArray = [NSMutableArray arrayWithCapacity:data.count];
    double shortMAvg = 0, longMAvg = 0;
    for (int i = 0; i < data.count; i++) {
        double close = [data[i][@"close"] doubleValue];
        if (i >= shortWindow) {
            shortMAvg = [[signalArray subarrayWithRange:NSMakeRange(i-shortWindow, shortWindow)] valueForKeyPath:@"@avg.self"];
        } else {
            shortMAvg = close;
        }
        [shortMAvgArray addObject:@(shortMAvg)];
        
        if (i >= longWindow) {
            longMAvg = [[signalArray subarrayWithRange:NSMakeRange(i-longWindow, longWindow)] valueForKeyPath:@"@avg.self"];
        } else {
            longMAvg = close;
        }
        [longMAvgArray addObject:@(longMAvg)];
        
        if (shortMAvg > longMAvg) {
            [signalArray addObject:@(1)];
        } else {
            [signalArray addObject:@(-1)];
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:shortMAvgArray forKey:@"short_mavg"];
    [signals setObject:longMAvgArray forKey:@"long_mavg"];
    return signals;
}

// 奇异值策略
- (NSDictionary *)anomalyStrategy:(NSDictionary *)data windowSize:(NSInteger)windowSize {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *sdArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *meanArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *upperBoundArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *lowerBoundArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *anomalyArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *rawData = [NSMutableArray arrayWithCapacity:windowSize];
    for (int i = 0; i < windowSize; i++) {
        [rawData addObject:data[i][@"close"]];
        [signalArray addObject:@(0)];
        [priceArray addObject:@([data[i][@"close"] doubleValue])];
        [sdArray addObject:@(0)];
        [meanArray addObject:@(0)];
        [upperBoundArray addObject:@(0)];
        [lowerBoundArray addObject:@(0)];
        [anomalyArray addObject:@(0)];
    }
    for (int i = windowSize; i < data.count; i++) {
        double sum = 0;
        double sqSum = 0;
        for (int j = 0; j < windowSize; j++) {
            double value = [data[i - j][@"close"] doubleValue];
            [rawData replaceObjectAtIndex:j withObject:@(value)];
            sum += value;
            sqSum += value * value;
        }
        double mean = sum / windowSize;
        double sd = sqrt(sqSum / windowSize - mean * mean);
        double upperBound = mean + 3 * sd;
        double lowerBound = mean - 3 * sd;
        double currentPrice = [data[i][@"close"] doubleValue];
        double anomaly = 0;
        for (int j = 0; j < windowSize; j++) {
            double value = [rawData[j] doubleValue];
            if (value > upperBound || value < lowerBound) {
                anomaly++;
            }
        }
        anomaly /= windowSize;
        if (currentPrice > upperBound && anomaly > 0.5) {
            [signalArray addObject:@(-1)];
        } else if (currentPrice < lowerBound && anomaly > 0.5) {
            [signalArray addObject:@(1)];
        } else {
            [signalArray addObject:@(0)];
        }
        [priceArray addObject:@([data[i][@"close"] doubleValue])];
        [sdArray addObject:@(sd)];
        [meanArray addObject:@(mean)];
        [upperBoundArray addObject:@(upperBound)];
        [lowerBoundArray addObject:@(lowerBound)];
        [anomalyArray addObject:@(anomaly)];
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    [signals setObject:sdArray forKey:@"sd"];
    [signals setObject:meanArray forKey:@"mean"];
    [signals setObject:upperBoundArray forKey:@"upper_bound"];
    [signals setObject:lowerBoundArray forKey:@"lower_bound"];
    [signals setObject:anomalyArray forKey:@"anomaly"];
    return signals;
}


// 移动平均线策略
- (NSDictionary *)movingAverageStrategy:(NSDictionary *)data shortWindow:(int)shortWindow longWindow:(int)longWindow {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *shortMAvgArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *longMAvgArray = [NSMutableArray arrayWithCapacity:data.count];
    double shortMAvg = 0, longMAvg = 0;
    for (int i = 0; i < data.count; i++) {
        double close = [data[i][@"close"] doubleValue];
        if (i >= shortWindow) {
            shortMAvg = [[signalArray subarrayWithRange:NSMakeRange(i-shortWindow, shortWindow)] valueForKeyPath:@"@avg.self"];
        } else {
            shortMAvg = close;
        }
        [shortMAvgArray addObject:@(shortMAvg)];
        
        if (i >= longWindow) {
            longMAvg = [[signalArray subarrayWithRange:NSMakeRange(i-longWindow, longWindow)] valueForKeyPath:@"@avg.self"];
        } else {
            longMAvg = close;
        }
        [longMAvgArray addObject:@(longMAvg)];
        
        if (shortMAvg > longMAvg) {
            [signalArray addObject:@(1)];
        } else {
            [signalArray addObject:@(-1)];
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:shortMAvgArray forKey:@"short_mavg"];
    [signals setObject:longMAvgArray forKey:@"long_mavg"];
    return signals;
}

// 均值回归
- (NSDictionary *)meanReversionStrategy:(NSDictionary *)data windowSize:(NSInteger)windowSize threshold:(double)threshold {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *movingAvgArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *movingStdArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *upperBandArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *lowerBandArray = [NSMutableArray arrayWithCapacity:data.count];
    BOOL longSignal = NO;
    BOOL shortSignal = NO;
    for (int i = 0; i < windowSize; i++) {
        [signalArray addObject:@(0)];
        [priceArray addObject:@([data[i][@"close"] doubleValue])];
        [movingAvgArray addObject:@(0)];
        [movingStdArray addObject:@(0)];
        [upperBandArray addObject:@(0)];
        [lowerBandArray addObject:@(0)];
    }
    for (int i = windowSize; i < data.count; i++) {
        double sum = 0;
        double sqSum = 0;
        for (int j = 0; j < windowSize; j++) {
            double value = [data[i - j][@"close"] doubleValue];
            sum += value;
            sqSum += value * value;
        }
        double movingAvg = sum / windowSize;
        double movingStd = sqrt(sqSum / windowSize - movingAvg * movingAvg);
        double upperBand = movingAvg + threshold * movingStd;
        double lowerBand = movingAvg - threshold * movingStd;
        double currentPrice = [data[i][@"close"] doubleValue];
        if (currentPrice < lowerBand && !longSignal) {
            [signalArray addObject:@(1)];
            longSignal = YES;
            shortSignal = NO;
        } else if (currentPrice > upperBand && !shortSignal) {
            [signalArray addObject:@(-1)];
            longSignal = NO;
            shortSignal = YES;
        } else {
            [signalArray addObject:@(0)];
            longSignal = NO;
            shortSignal = NO;
        }
        [priceArray addObject:@(currentPrice)];
        [movingAvgArray addObject:@(movingAvg)];
        [movingStdArray addObject:@(movingStd)];
        [upperBandArray addObject:@(upperBand)];
        [lowerBandArray addObject:@(lowerBand)];
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    [signals setObject:movingAvgArray forKey:@"moving_avg"];
    [signals setObject:movingStdArray forKey:@"moving_std"];
    [signals setObject:upperBandArray forKey:@"upper_band"];
    [signals setObject:lowerBandArray forKey:@"lower_band"];
    return signals;
}


// 统计套利
- (NSDictionary *)statArbStrategy:(NSDictionary *)data1 data2:(NSDictionary *)data2 windowSize:(int)windowSize threshold:(double)threshold {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data1.count];
    NSMutableArray *spreadArray = [NSMutableArray arrayWithCapacity:data1.count];
    for (int i = 0; i < data1.count; i++) {
        double price1 = [data1[i][@"close"] doubleValue];
        double price2 = [data2[i][@"close"] doubleValue];
        if (i < windowSize) {
            [signalArray addObject:@(0)];
            [spreadArray addObject:@(0)];
        } else {
            double spread = price1 - price2;
            double meanSpread = [[spreadArray subarrayWithRange:NSMakeRange(i-windowSize, windowSize)] valueForKeyPath:@"@avg.self"];
            double stdSpread = [[spreadArray subarrayWithRange:NSMakeRange(i-windowSize, windowSize)] valueForKeyPath:@"@stddev.self"];
            double zScore = (spread - meanSpread) / stdSpread;
            [spreadArray addObject:@(spread)];
            if (zScore > threshold) {
                [signalArray addObject:@(-1)];
            } else if (zScore < -threshold) {
                [signalArray addObject:@(1)];
            } else {
                [signalArray addObject:@(0)];
            }
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:spreadArray forKey:@"spread"];
    return signals;
}

// 市场情绪
- (NSDictionary *)marketSentimentStrategy:(NSDictionary *)data windowSize:(int)windowSize threshold:(double)threshold {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    double meanPrice = 0, stdPrice = 0;
    for (int i = 0; i < data.count; i++) {
        double price = [data[i][@"close"] doubleValue];
        [priceArray addObject:@(price)];
        if (i >= windowSize) {
            NSArray *windowPrices = [priceArray subarrayWithRange:NSMakeRange(i-windowSize, windowSize)];
            meanPrice = [windowPrices valueForKeyPath:@"@avg.self"];
            stdPrice = [windowPrices valueForKeyPath:@"@stddev.self"];
            double zScore = (price - meanPrice) / stdPrice;
            if (zScore > threshold) {
                [signalArray addObject:@(1)];
            } else if (zScore < -threshold) {
                [signalArray addObject:@(-1)];
            } else {
                [signalArray addObject:@(0)];
            }
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    return signals;
}


// 支持阻力策略
//在这个示例中，我们首先确定支撑和阻力水平，并根据它们来确定交易信号。如果价格突破阻力水平，则建立多头头寸，如果价格跌破支撑水平，则建立空头头寸。我们还可以根据支撑和阻力水平的数量和位置来优化策略。
- (NSDictionary *)supportResistanceStrategy:(NSDictionary *)data support:(double)support resistance:(double)resistance {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    BOOL longSignal = NO;
    BOOL shortSignal = NO;
    for (int i = 0; i < data.count; i++) {
        double currentPrice = [data[i][@"close"] doubleValue];
        if (currentPrice > resistance && !longSignal) {
            [signalArray addObject:@(1)];
            longSignal = YES;
            shortSignal = NO;
        } else if (currentPrice < support && !shortSignal) {
            [signalArray addObject:@(-1)];
            longSignal = NO;
            shortSignal = YES;
        } else {
            [signalArray addObject:@(0)];
            longSignal = NO;
            shortSignal = NO;
        }
        [priceArray addObject:@(currentPrice)];
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    return signals;
}



// 震荡指标策略
- (NSDictionary *)oscillatorStrategy:(NSDictionary *)data windowSize:(int)windowSize threshold:(double)threshold {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *rocArray = [NSMutableArray arrayWithCapacity:data.count];
    double prevPrice = 0;
    for (int i = 0; i < data.count; i++) {
        double price = [data[i][@"close"] doubleValue];
        if (i > 0) {
            double roc = (price - prevPrice) / prevPrice;
            [rocArray addObject:@(roc)];
        } else {
            [rocArray addObject:@(0)];
        }
        prevPrice = price;
        [priceArray addObject:@(price)];
        if (i >= windowSize) {
            NSArray *windowROC = [rocArray subarrayWithRange:NSMakeRange(i-windowSize, windowSize)];
            double meanROC = [windowROC valueForKeyPath:@"@avg.self"];
            double stdROC = [windowROC valueForKeyPath:@"@stddev.self"];
            double zScore = (roc - meanROC) / stdROC;
            if (zScore > threshold) {
                [signalArray addObject:@(1)];
            } else if (zScore < -threshold) {
                [signalArray addObject:@(-1)];
            } else {
                [signalArray addObject:@(0)];
            }
        } else {
            [signalArray addObject:@(0)];
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    [signals setObject:rocArray forKey:@"roc"];
    return signals;
}

// KDJ指标策略
//KDJ指标是一种基于价格和时间分析的技术指标，用于判断股票市场的超买和超卖状态。它是由三条曲线组成的：K线、D线和J线。KDJ指标可以通过以下公式计算：

//RSV = (收盘价 - 最低价) / (最高价 - 最低价) * 100
//K = 2/3 * 前一日K值 + 1/3 * 当日RSV
//D = 2/3 * 前一日D值 + 1/3 * 当日K值
//J = 3 * 当日K值 - 2 * 当日D值
- (NSDictionary *)kdjStrategy:(NSDictionary *)data n:(NSInteger)n {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *kArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *dArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *jArray = [NSMutableArray arrayWithCapacity:data.count];
    double high = [data[0][@"high"] doubleValue];
    double low = [data[0][@"low"] doubleValue];
    double rsv = 0;
    double k = 50;
    double d = 50;
    double j = 50;
    for (int i = 0; i < data.count; i++) {
        double currentPrice = [data[i][@"close"] doubleValue];
        high = MAX(high, [data[i][@"high"] doubleValue]);
        low = MIN(low, [data[i][@"low"] doubleValue]);
        if (i >= n - 1) {
            rsv = (currentPrice - low) / (high - low) * 100;
            k = 2.0 / 3 * k + 1.0 / 3 * rsv;
            d = 2.0 / 3 * d + 1.0 / 3 * k;
            j = 3 * k - 2 * d;
        }
        [kArray addObject:@(k)];
        [dArray addObject:@(d)];
        [jArray addObject:@(j)];
        if (k < d && k < j) {
            [signalArray addObject:@(-1)];
        } else if (k > d && k > j) {
            [signalArray addObject:@(1)];
        } else {
            [signalArray addObject:@(0)];
        }
        [priceArray addObject:@(currentPrice)];
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    [signals setObject:kArray forKey:@"k"];
    [signals setObject:dArray forKey:@"d"];
    [signals setObject:jArray forKey:@"j"];
    return signals;
}


// 交叉验证策略
- (NSDictionary *)crossValidationStrategy:(NSDictionary *)data trainWindowSize:(int)trainWindowSize testWindowSize:(int)testWindowSize threshold:(double)threshold {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    double meanPrice = 0, stdPrice = 0;
    for (int i = 0; i < data.count; i++) {
        double price =
        [priceArray addObject:@(price)];
        meanPrice = i == 0 ? price : (i * meanPrice + price) / (i + 1);
        stdPrice = i == 0 ? 0 : sqrt(((i-1)*stdPrice*stdPrice + (price-meanPrice)*(price-meanPrice)) / i);
        if (i >= trainWindowSize + testWindowSize) {
            NSArray *trainPrices = [priceArray subarrayWithRange:NSMakeRange(i-testWindowSize-trainWindowSize, trainWindowSize)];
            NSArray *testPrices = [priceArray subarrayWithRange:NSMakeRange(i-testWindowSize, testWindowSize)];
            double meanTrainPrice = [trainPrices valueForKeyPath:@"@avg.self"];
            double stdTrainPrice = [trainPrices valueForKeyPath:@"@stddev.self"];
            double upperThreshold = meanTrainPrice + stdTrainPrice * threshold;
            double lowerThreshold = meanTrainPrice - stdTrainPrice * threshold;
            double meanTestPrice = [testPrices valueForKeyPath:@"@avg.self"];
            if (meanTestPrice > upperThreshold) {
                [signalArray addObject:@(-1)];
            } else if (meanTestPrice < lowerThreshold) {
                [signalArray addObject:@(1)];
            } else {
                [signalArray addObject:@(0)];
            }
        } else {
            [signalArray addObject:@(0)];
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    return signals;
}

// 单层决策树策略

- (NSDictionary *)decisionTreeStrategy:(NSDictionary *)data windowSize:(int)windowSize threshold:(double)threshold {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *returnArray = [NSMutableArray arrayWithCapacity:data.count];
    for (int i = 0; i < data.count; i++) {
        double price = [data[i][@"close"] doubleValue];
        [priceArray addObject:@(price)];
        double prevPrice = i == 0 ? price : [priceArray[i-1] doubleValue];
        double returnRate = (price - prevPrice) / prevPrice;
        [returnArray addObject:@(returnRate)];
        if (i >= windowSize) {
            NSArray *windowReturns = [returnArray subarrayWithRange:NSMakeRange(i-windowSize, windowSize)];
            double meanReturn = [windowReturns valueForKeyPath:@"@avg.self"];
            if (meanReturn > threshold) {
                [signalArray addObject:@(1)];
            } else if (meanReturn < -threshold) {
                [signalArray addObject:@(-1)];
            } else {
                [signalArray addObject:@(0)];
            }
        } else {
            [signalArray addObject:@(0)];
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    [signals setObject:returnArray forKey:@"return"];
    return signals;
}

// 均值回归策略
- (NSDictionary *)meanReversionStrategy:(NSDictionary *)data windowSize:(int)windowSize threshold:(double)threshold {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *zscoreArray = [NSMutableArray arrayWithCapacity:data.count];
    double prevPrice = 0;
    for (int i = 0;
     double price = [data[i][@"close"] doubleValue];
     [priceArray addObject:@(price)];
     if (i >= windowSize) {
         NSArray *windowPrices = [priceArray subarrayWithRange:NSMakeRange(i-windowSize, windowSize)];
         double meanPrice = [windowPrices valueForKeyPath:@"@avg.self"];
         double stdPrice = [windowPrices valueForKeyPath:@"@stddev.self"];
         double zscore = (price - meanPrice) / stdPrice;
         [zscoreArray addObject:@(zscore)];
         if (zscore > threshold) {
             [signalArray addObject:@(-1)];
         } else if (zscore < -threshold) {
             [signalArray addObject:@(1)];
         } else {
             [signalArray addObject:@(0)];
         }
     } else {
         [zscoreArray addObject:@(0)];
         [signalArray addObject:@(0)];
     }
     prevPrice = price;
 }
 [signals setObject:signalArray forKey:@"signal"];
 [signals setObject:priceArray forKey:@"price"];
 [signals setObject:zscoreArray forKey:@"zscore"];
 return signals;
}

// 基本面分析
- (NSDictionary *)fundamentalAnalysisStrategy:(NSDictionary *)data windowSize:(int)windowSize threshold:(double)threshold {
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *peRatioArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *pbRatioArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *roeArray = [NSMutableArray arrayWithCapacity:data.count];
    for (int i = 0; i < data.count; i++) {
        double price = [data[i][@"close"] doubleValue];
        [priceArray addObject:@(price)];
        double peRatio = [data[i][@"pe_ratio"] doubleValue];
        [peRatioArray addObject:@(peRatio)];
        double pbRatio = [data[i][@"pb_ratio"] doubleValue];
        [pbRatioArray addObject:@(pbRatio)];
        double roe = [data[i][@"roe"] doubleValue];
        [roeArray addObject:@(roe)];
        if (i >= windowSize) {
            NSArray *windowPeRatio = [peRatioArray subarrayWithRange:NSMakeRange(i-windowSize, windowSize)];
            NSArray *windowPbRatio = [pbRatioArray subarrayWithRange:NSMakeRange(i-windowSize, windowSize)];
            NSArray *windowRoe = [roeArray subarrayWithRange:NSMakeRange(i-windowSize, windowSize)];
            double meanPeRatio = [windowPeRatio valueForKeyPath:@"@avg.self"];
            double meanPbRatio = [windowPbRatio valueForKeyPath:@"@avg.self"];
            double meanRoe = [windowRoe valueForKeyPath:@"@avg.self"];
            if (peRatio < meanPeRatio * (1 - threshold) && pbRatio < meanPbRatio * (1 - threshold) && roe > meanRoe * (1 + threshold)) {
                [signalArray addObject:@(1)];
            } else if (peRatio > meanPeRatio * (1 + threshold) && pbRatio > meanPbRatio * (1 + threshold) && roe < meanRoe * (1 - threshold)) {
                [signalArray addObject:@(-1)];
            } else {
                [signalArray addObject:@(0)];
            }
        } else {
            [signalArray addObject:@(0)];
        }
    }
    [signals setObject:signalArray forKey:@"signal"];
 [signals setObject:priceArray forKey:@"price"];
 [signals setObject:peRatioArray forKey:@"pe_ratio"];
 [signals setObject:pbRatioArray forKey:@"pb_ratio"];
 [signals setObject:roeArray forKey:@"roe"];
 return signals;
}

// 组合策略
- (NSDictionary *)combinationStrategy:(NSDictionary *)data {
    NSDictionary *signals1 = [self movingAverageStrategy:data windowSize:5];
    NSDictionary *signals2 = [self momentumStrategy:data windowSize:5];
    NSDictionary *signals3 = [self intradayStrategy:data];
    NSDictionary *signals4 = [self breakoutStrategy:data windowSize:10 threshold:1.5];
    NSDictionary *signals5 = [self reversalStrategy:data windowSize:10 threshold:1.5];
    NSMutableDictionary *signals = [NSMutableDictionary dictionary];
    NSMutableArray *signalArray = [NSMutableArray arrayWithCapacity:data.count];
    NSMutableArray *priceArray = [NSMutableArray arrayWithCapacity:data.count];
    for (int i = 0; i < data.count; i++) {
        double signal1 = [signals1[@"signal"][i] doubleValue];
        double signal2 = [signals2[@"signal"][i] doubleValue];
        double signal3 = [signals3[@"signal"][i] doubleValue];
        double signal4 = [signals4[@"signal"][i] doubleValue];
        double signal5 = [signals5[@"signal"][i] doubleValue];
        double signal = signal1 + signal2 + signal3 + signal4 + signal5;
        if (signal > 0) {
            [signalArray addObject:@(1)];
        } else if (signal < 0) {
            [signalArray addObject:@(-1)];
        } else {
            [signalArray addObject:@(0)];
        }
        [priceArray addObject:@([data[i][@"close"] doubleValue])];
    }
    [signals setObject:signalArray forKey:@"signal"];
    [signals setObject:priceArray forKey:@"price"];
    return signals;
}

// 海龟策略
// 海龟交易策略是一种经典的趋势跟随策略，它主要基于价格突破和动态风险控制来实现交易
- (void)turtleTradingStrategy:(NSArray *)data {
    double entryPrice = 0.0;
    double stopLossPrice = 0.0;
    double profitTargetPrice = 0.0;
    double maxPrice = 0.0;
    double minPrice = 0.0;
    double atr = 0.0;
    NSInteger position = 0;
    for (NSInteger i = 0; i < data.count; i++) {
        double currentPrice = [data[i][@"close"] doubleValue];
        if (position == 0) {
            if (currentPrice > maxPrice) {
                maxPrice = currentPrice;
            }
            if (currentPrice < minPrice) {
                minPrice = currentPrice;
            }
            if (i > 19) {
                atr = [self calculateATRWithData:data currentIndex:i];
                entryPrice = maxPrice + 2 * atr;
                stopLossPrice = minPrice - 2 * atr;
                profitTargetPrice = entryPrice + 2 * atr;
                if (currentPrice > entryPrice) {
                    position = 1;
                    [self buyWithPrice:currentPrice];
                } else if (currentPrice < stopLossPrice) {
                    position = -1;
                    [self sellWithPrice:currentPrice];
                }
            }
        } else if (position == 1) {
            if (currentPrice > maxPrice) {
                maxPrice = currentPrice;
            }
            if (currentPrice < stopLossPrice) {
                position = 0;
                [self sellWithPrice:currentPrice];
            } else if (currentPrice > profitTargetPrice) {
                position = 0;
                [self sellWithPrice:currentPrice];
            }
        } else if (position == -1) {
            if (currentPrice < minPrice) {
                minPrice = currentPrice;
            }
            if (currentPrice > stopLossPrice) {
                position = 0;
                [self buyWithPrice:currentPrice];
            } else if (currentPrice < profitTargetPrice) {
                position = 0;
                [self buyWithPrice:currentPrice];
            }
        }
    }
    if (position == 1) {
        [self sellWithPrice:[data.lastObject[@"close"] doubleValue]];
    } else if (position == -1) {
        [self buyWithPrice:[data.lastObject[@"close"] doubleValue]];
    }
}

- (double)calculateATRWithData:(NSArray *)data currentIndex:(NSInteger)currentIndex {
    // 计算ATR
}

- (void)buyWithPrice:(double)price {
    // 买入
}

- (void)sellWithPrice:(double)price {
    // 卖出
}


#pragma 统计套利
- (void)statisticalArbitrageStrategy:(NSDictionary *)data1 data2:(NSDictionary *)data2 {
    double currentPrice1 = [data1[@"close"] doubleValue];
    double currentPrice2 = [data2[@"close"] doubleValue];
    double meanPrice1 = [self calculateMeanPriceWithData:data1];
    double meanPrice2 = [self calculateMeanPriceWithData:data2];
    double stdPrice1 = [self calculateStdPriceWithData:data1 meanPrice:meanPrice1];
    double stdPrice2 = [self calculateStdPriceWithData:data2 meanPrice:meanPrice2];
    if (currentPrice1 - meanPrice1 > 2 * stdPrice1 && currentPrice2 - meanPrice2 < -2 * stdPrice2) {
        [self sellWithPrice:currentPrice1 buyWithPrice:currentPrice2];
    } else if (currentPrice1 - meanPrice1 < -2 * stdPrice1 && currentPrice2 - meanPrice2 > 2 * stdPrice2) {
        [self buyWithPrice:currentPrice1 sellWithPrice:currentPrice2];
    }
}

- (double)calculateMeanPriceWithData:(NSDictionary *)data {
    // 计算平均价格
}

- (double)calculateStdPriceWithData:(NSDictionary *)data meanPrice:(double)meanPrice {
    // 计算价格标准差
}

- (void)buyWithPrice:(double)price1 sellWithPrice:(double)price2 {
    // 买入price1，卖出price2
}

- (void)sellWithPrice:(double)price1 buyWithPrice:(double)price2 {
    // 卖出price1，买入price2
}


@end
