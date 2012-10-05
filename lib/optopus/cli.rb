require 'optopus/api'
require 'optparse'
module Optopus
  module CLI
    def self.run
      options.endpoint = ENV['OPTOPUS_ENDPOINT']
      command = ARGV.shift
      usage if command.nil?
      command = command.to_sym
      usage unless self.respond_to?(command)
      self.send(command, ARGV)
    end

    def self.usage
      puts "Usage: #{$0} find $query"
      exit 1
    end

    def self.find(args)
      parse_find_opts(args)
      usage if args.empty?
      types = [ 'node', 'hypervisor', 'network_node' ]
      api = Optopus::API.new(options.endpoint)
      api.search(args.join(' '), types).each do |item|
        puts item['hostname']
        if options.facts
          options.facts.each do |fact|
            printf "%15s: %s\n", fact, item['facts'][fact]
          end
          puts
        end
      end
    end

    private

    def self.parse_find_opts(args)
      opts = OptionParser.new do |opts|
        opts.banner = "Usage: #{$0} find [options]"
        opts.on('-F', '--facts FACTS', 'Comma separated list of facts to display about each result') do |facts|
          options.facts = facts.split(',')
        end
      end
      opts.parse!(args)
    end

    def self.options
      @options ||= OpenStruct.new
    end
  end
end
